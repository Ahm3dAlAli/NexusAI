import { AgentMessageType } from "@prisma/client";

export interface AgentMessage {
  order: number;
  type: AgentMessageType;
  content: string;
  tool_name?: string;
  urls?: string[] | null;
}
