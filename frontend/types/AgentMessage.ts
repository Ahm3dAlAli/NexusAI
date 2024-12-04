export enum AgentMessageType {
    system = "system",
    human = "human",
    agent = "agent",
    tool = "tool",
    error = "error",
    final = "final",
  }
  
  export interface AgentMessage {
    type: AgentMessageType;
    content: string;
    tool_name?: string;
  }