import { AuthOptions } from "next-auth"
import CredentialsProvider from "next-auth/providers/credentials"
import AzureADProvider from "next-auth/providers/azure-ad"
import { prisma } from "@/lib/prisma"
import { compare } from "bcrypt"
import { DefaultSession } from "next-auth"

declare module "next-auth" {
  interface Session {
    user: {
      id: string
      email: string
      name: string
    } & Omit<DefaultSession["user"], "email" | "name">
  }
}

export const authOptions: AuthOptions = {
  providers: [
    CredentialsProvider({
      name: "Credentials",
      credentials: {
        email: { label: "Email", type: "email", placeholder: "john@example.com" },
        password: { label: "Password", type: "password" }
      },
      async authorize(credentials) {
        if (!credentials?.email || !credentials?.password) {
          throw new Error("Email and password required")
        }

        const user = await prisma.user.findUnique({
          where: { email: credentials.email }
        })

        if (!user) {
          throw new Error("No user found with the given email")
        }
        if (!user.password) {
          throw new Error("Invalid credentials")
        }
        const isValid = await compare(credentials.password, user.password)

        if (!isValid) {
          throw new Error("Invalid password")
        }

        return { id: user.id, name: user.name, email: user.email }
      }
    }),
    AzureADProvider({
      clientId: process.env.AZURE_AD_CLIENT_ID!,
      clientSecret: process.env.AZURE_AD_CLIENT_SECRET!,
      tenantId: process.env.AZURE_AD_TENANT_ID!,
      authorization: {
        params: {
          scope: "openid profile email"
        }
      }
    })
  ],
  callbacks: {
    async signIn({ user, account, profile }) {
      if (account?.provider === "azure-ad") {
        if (!profile?.email) {
          console.warn("Azure AD sign-in attempted without an email.")
          return false
        }

        try {
          const existingUser = await prisma.user.findUnique({
            where: { email: profile.email }
          })

          if (existingUser) {
            if (existingUser.password) {
              // Prevent account creation if email exists with credentials
              console.warn(`Sign-in with Azure AD attempted for existing email: ${profile.email} which has a credentials-based account.`)
              return false
            } else {
              // Existing Azure AD user, proceed with sign-in
              user.id = existingUser.id
              return true
            }
          } else {
            // No existing user, create new Azure AD user
            const newUser = await prisma.user.create({
              data: {
                name: profile.name || profile.email,
                email: profile.email,
                password: null // Azure AD users don't need a password
              }
            })
            user.id = newUser.id
            console.info(`New Azure AD user created: ${profile.email}`)
            return true
          }
        } catch (error) {
          console.error("Error during Azure AD sign-in:", error)
          return false
        }
      }
      return true
    },
    async jwt({ token, user }) {
      if (user) {
        token.id = user.id
      }
      return token
    },
    async session({ session, token }) {
      if (token && session.user) {
        session.user.id = token.id as string
      }
      return session
    }
  },
  pages: {
    signIn: "/login",
    signOut: "/",
    error: "/login",
  },
  session: {
    strategy: "jwt",
    maxAge: 7 * 24 * 60 * 60,
    updateAge: 24 * 60 * 60,
  }
}
