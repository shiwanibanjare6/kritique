from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.pull_request_repository import PullRequestRepository
from app.repositories.repository_repository import RepositoryRepository
from app.repositories.webhook_repository import WebhookRepository
from app.repositories.pull_request_file_repository import PullRequestFileRepository
from app.repositories.review_repository import ReviewRepository

from app.services.github_service import GitHubService
from app.services.ai_review_service import AIReviewService

class WebhookService:

    def __init__(self, db: AsyncSession):

        self.db = db

        self.repository_repo = RepositoryRepository(db)
        self.pull_request_repo = PullRequestRepository(db)
        self.pull_request_file_repo = PullRequestFileRepository(db)
        self.webhook_repo = WebhookRepository(db)
        self.review_repo = ReviewRepository(db)

        self.github_service = GitHubService()
        self.ai_review = AIReviewService()
         
    async def process_pull_request(
        self,
        payload: dict,
        event_type: str,
        delivery_id: str,
    ):
        print("=" * 50)
        print("Webhook received")
        print(event_type)
        print(payload.get("action"))
        print("=" * 50)

        if "pull_request" not in payload:
            return {
                "status": "ignored",
                "reason": "Not a pull_request event",
            }

        repo_data = payload["repository"]

        repository = await self.repository_repo.get_by_github_id(
            repo_data["id"]
        )

        if repository is None:

            repository = await self.repository_repo.create(
                github_id=repo_data["id"],
                owner=repo_data["owner"]["login"],
                name=repo_data["name"],
                full_name=repo_data["full_name"],
                default_branch=repo_data["default_branch"],
            )

        existing_event = await self.webhook_repo.get_by_delivery_id(
            delivery_id
        )

        if existing_event:
            print(f"Webhook {delivery_id} already processed.")
            return {
                "status": "duplicate",
                "delivery_id": delivery_id,
            }

        await self.webhook_repo.create(
            repository_id=repository.id,
            delivery_id=delivery_id,
            event_type=event_type,
            payload=payload,
        )
        pr = payload["pull_request"]
        print("Pull Request Found")

        existing_pr = await self.pull_request_repo.get_by_github_id(
            pr["id"]
        )

        if existing_pr is None:

            saved_pr = await self.pull_request_repo.create(
                repository_id=repository.id,
                github_pr_id=pr["id"],
                html_url=pr["html_url"],
                pr_number=pr["number"],
                title=pr["title"],
                author=pr["user"]["login"],
                state=pr["state"],
                base_branch=pr["base"]["ref"],
                head_branch=pr["head"]["ref"],
            )

        else:

            saved_pr = existing_pr

        files = await self.github_service.get_pull_request_files(
            repository.owner,
            repository.name,
            saved_pr.pr_number,
        )
        
        print(files)
        print(len(files))

        await self.pull_request_file_repo.delete_by_pr(
            saved_pr.id
        )

        overall_summary = []

        review_scores = {
            "security_score": 0,
            "style_score": 0,
            "architecture_score": 0,
            "final_score": 0,
        }

        all_comments = []

        all_agent_output = []
        for file in files:

            # Save PR file
            await self.pull_request_file_repo.create(
                pull_request_id=saved_pr.id,
                filename=file["filename"],
                status=file["status"],
                additions=file["additions"],
                deletions=file["deletions"],
                changes=file["changes"],
                patch=file.get("patch"),
            )

            # AI Review
            print(file["filename"])
            review = await self.ai_review.review_code(
                filename=file["filename"],
                patch=file.get("patch"),
            )

            all_agent_output.append(
                {
                    "file": file["filename"],
                    "review": review,
                }
            )

            overall_summary.append(
                f"## {file['filename']}\n\n{review['summary']}"
            )

            review_scores["security_score"] += review.get(
                "security_score", 0
            )
            review_scores["style_score"] += review.get(
                "style_score", 0
            )
            review_scores["architecture_score"] += review.get(
                "architecture_score", 0
            )
            review_scores["final_score"] += review.get(
                "final_score", 0
            )

            for comment in review.get("comments", []):

                github_comment = {
                    "path": file["filename"],
                    "line": comment["line"],
                    "side": "RIGHT",
                    "body": (
                        f"**{comment['severity'].upper()}**\n\n"
                        f"{comment['comment']}"
                    ),
                }

                all_comments.append(github_comment)

        file_count = max(len(files), 1)

        summary = "\n\n".join(overall_summary)

        security_score = review_scores["security_score"] / file_count
        style_score = review_scores["style_score"] / file_count
        architecture_score = (
            review_scores["architecture_score"] / file_count
        )
        final_score = review_scores["final_score"] / file_count

        await self.review_repo.create(
            pull_request_id=saved_pr.id,
            summary=summary,
            security_score=security_score,
            style_score=style_score,
            architecture_score=architecture_score,
            final_score=final_score,
            agent_output=all_agent_output,
        )

        print("\n" + "=" * 80)
        print("AI REVIEW")
        print("=" * 80)
        print(summary)
        print("=" * 80)

        await self.github_service.create_review(
            owner=repository.owner,
            repo=repository.name,
            pull_number=saved_pr.pr_number,
            body=summary,
            comments=all_comments if all_comments else None,
        )

        return {
            "status": "saved",
            "repository": repository.full_name,
            "pull_request": saved_pr.pr_number,
            "files_processed": len(files),
            "overall_score": round(final_score, 2),
        }