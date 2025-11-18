import { contextBridge, ipcRenderer } from 'electron';
import type { RendererAPI, OpenDialogResult } from '../common/types';

const api: RendererAPI & {
  getFileInfo?: (path: string) => Promise<{ size: number }>;
} = {
  ping: () => ipcRenderer.invoke('ping'),
  pickVideo: (): Promise<OpenDialogResult> => ipcRenderer.invoke('dialog:openVideo'),
  pickDirectory: (): Promise<OpenDialogResult> => ipcRenderer.invoke('dialog:openDirectory'),
  config: {
    read: () => ipcRenderer.invoke('config:read'),
    write: (data) => ipcRenderer.invoke('config:write', data),
  },
  getFileInfo: (path: string) => ipcRenderer.invoke('file:getInfo', path),
};

contextBridge.exposeInMainWorld('api', api);