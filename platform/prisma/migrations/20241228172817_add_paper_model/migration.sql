-- CreateEnum
CREATE TYPE "ProcessingStatus" AS ENUM ('not_started', 'processing', 'done', 'failed');

-- CreateTable
CREATE TABLE "Paper" (
    "id" TEXT NOT NULL,
    "title" TEXT NOT NULL,
    "authors" TEXT NOT NULL,
    "summary" TEXT NOT NULL,
    "url" TEXT NOT NULL,
    "processingStatus" "ProcessingStatus" NOT NULL DEFAULT 'not_started',
    "userId" TEXT,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "Paper_pkey" PRIMARY KEY ("id")
);

-- AddForeignKey
ALTER TABLE "Paper" ADD CONSTRAINT "Paper_userId_fkey" FOREIGN KEY ("userId") REFERENCES "User"("id") ON DELETE SET NULL ON UPDATE CASCADE;
