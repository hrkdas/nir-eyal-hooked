// Sample Workspace Model demonstrating Stored Value & IKEA effect commitment
export interface UserWorkspace {
  id: string;
  userId: string;
  // Stored Value 1: Content accumulation
  userCreatedDocuments: string[];
  // Stored Value 2: Personal data / preferences
  customTags: string[];
  // Stored Value 3: Follower / peer network
  collaborators: string[];
  // Stored Value 4: Skill & Reputation level
  masteryPoints: number;
}

export function saveUserDocument(workspace: UserWorkspace, doc: string) {
  workspace.userCreatedDocuments.push(doc);
  // Stored value appreciation: Product becomes more valuable with every use
  return workspace;
}
