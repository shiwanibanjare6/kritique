import { signIn } from "@/auth";
import { GitBranch } from "lucide-react";

export default function LoginPage() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-muted/30 px-4">
      <div className="w-full max-w-md rounded-xl border bg-background p-8 shadow-lg">
        <div className="mb-8 text-center">
          <h1 className="text-3xl font-bold">Kritique.ai</h1>

          <p className="mt-2 text-muted-foreground">
            AI-powered GitHub Pull Request Reviews
          </p>
        </div>

        <form
          action={async () => {
            "use server";
            await signIn("github", {
              redirectTo: "/",
            });
          }}
        >
          <button
            type="submit"
            className="flex w-full items-center justify-center gap-2 rounded-lg bg-black px-4 py-3 font-medium text-white transition hover:opacity-90 dark:bg-white dark:text-black"
          >
            <GitBranch className="h-5 w-5" />
            Continue with GitHub
          </button>
        </form>

        <p className="mt-6 text-center text-sm text-muted-foreground">
          Secure authentication powered by GitHub
        </p>
      </div>
    </div>
  );
}