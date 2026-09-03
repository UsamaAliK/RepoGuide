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
