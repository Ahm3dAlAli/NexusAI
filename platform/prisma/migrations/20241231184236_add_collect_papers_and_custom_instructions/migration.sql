-- AlterTable
ALTER TABLE "User" ADD COLUMN     "collectPapers" BOOLEAN NOT NULL DEFAULT true,
ADD COLUMN     "customInstructions" TEXT[] DEFAULT ARRAY[]::TEXT[];
