import { AuthOptions } from "next-auth"
import CredentialsProvider from "next-auth/providers/credentials"
import AzureADProvider from "next-auth/providers/azure-ad"
import { prisma } from "@/lib/prisma"
import { compare } from "bcrypt"
import { User as PrismaUser } from "@prisma/client"

declare module "next-auth" {
  interface Session {
    user: PrismaUser
  }

  interface User extends PrismaUser {
    password: string | null
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

        return user
      }
    }),
    AzureADProvider({
      clientId: process.env.AZURE_AD_CLIENT_ID!,
      clientSecret: process.env.AZURE_AD_CLIENT_SECRET!,
      tenantId: "common",
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
              console.warn(`Sign-in with Azure AD attempted for existing email: ${profile.email} which has a credentials-based account.`)
              return false
            } else {
              user.id = existingUser.id
              user.password = null
              return true
            }
          } else {
            const newUser = await prisma.user.create({
              data: {
                name: profile.name || profile.email,
                email: profile.email,
                password: null
              }
            })
            user.id = newUser.id
            user.password = null
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
        token.user = user
      }
      return token
    },
    async session({ session, token }) {
      if (token.user) {
        session.user = token.user as PrismaUser
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
