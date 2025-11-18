export type OpenDialogResult = { canceled: boolean; filePaths: string[] };

export interface RendererAPI {
  ping: () => Promise<string>;
  pickVideo: () => Promise<OpenDialogResult>;
  pickDirectory: () => Promise<OpenDialogResult>;
  config: {
    read: () => Promise<Record<string, any> | null>;
    write: (data: Record<string, any>) => Promise<boolean>;
  };
  getFileInfo?: (path: string) => Promise<{ size: number }>;
}

declare global {
  interface Window { api?: RendererAPI }
}