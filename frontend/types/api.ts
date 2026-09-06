export type IndexRepositoryResponse = {
  url: string;
  status: string;
  message: string;
  file_count: number;
};

export type Source = {
  file_path: string;
  start_line: number;
  end_line: number;
  commit_sha: string;
  score: number;
};

export type AskResponse = {
  answer: string;
  sources: Source[];
};

export type ChatResponse = {
  answer: string;
  conversation_id: number;
  sources: Source[];
};

export type RepositoryInfo = {
  id: number;
  github_url: string;
  owner: string;
  repo_name: string;
  branch: string;
  commit_sha: string;
  status: string;
  created_at: string;
};

export type Conversation = {
  id: number;
  repository_id: number;
  title: string;
  created_at: string;
  updated_at: string;
};

export type Message = {
  id: number;
  role: string;
  content: string;
  created_at: string;
  sources: Source[];
};

export type RegisterRequest = {
  username: string;
  password: string;
};

export type LoginRequest = {
  username: string;
  password: string;
};

export type TokenResponse = {
  access_token: string;
  token_type: string;
};
