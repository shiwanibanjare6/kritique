import NextAuth from "next-auth";
import GitHub from "next-auth/providers/github";

function resolveAuthUrl() {
  if (process.env.VERCEL_ENV === "production") {
    const productionHost =
      process.env.VERCEL_PROJECT_PRODUCTION_URL ?? "kritique-three.vercel.app";
    return new URL(
      productionHost.startsWith("http")
        ? productionHost
        : `https://${productionHost}`,
    ).origin;
  }

  if (process.env.VERCEL_URL) {
    return new URL(`https://${process.env.VERCEL_URL}`).origin;
  }

  return "http://localhost:3000";
}

// AUTH_URL takes precedence over the legacy NEXTAUTH_URL in Auth.js v5.
// Set it before NextAuth initializes so stale deployment URLs cannot affect
// the OAuth callback URI.
process.env.AUTH_URL = resolveAuthUrl();

export const { handlers, auth, signIn, signOut } = NextAuth({
  trustHost: true,
  providers: [
    GitHub({
      clientId: process.env.AUTH_GITHUB_ID!,
      clientSecret: process.env.AUTH_GITHUB_SECRET!,
      authorization: {
        params: {
          scope: "read:user user:email repo read:org",
          prompt: "select_account",
        },
      },
    }),
  ],

  pages: {
    signIn: "/login",
  },

  callbacks: {
    async jwt({ token, account }) {
      if (account?.access_token) {
        token.accessToken = account.access_token;
      }

      return token;
    },

    async session({ session, token }) {
      session.accessToken = token.accessToken as string;

      return session;
    },
  },
});
