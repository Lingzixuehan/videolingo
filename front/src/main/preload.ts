import { contextBridge, ipcRenderer } from 'electron';
import type { OpenDialogResult } from '../common/types';

// expose a permissive API shape (use `any` so we can add methods without hitting type errors)
const api: any = {
  ping: () => ipcRenderer.invoke('ping'),
  pickVideo: (): Promise<OpenDialogResult> => ipcRenderer.invoke('dialog:openVideo'),
  pickDirectory: (): Promise<OpenDialogResult> => ipcRenderer.invoke('dialog:openDirectory'),
  config: {
    read: () => ipcRenderer.invoke('config:read'),
    write: (data: any) => ipcRenderer.invoke('config:write', data),
  },
  getFileInfo: (path: string) => ipcRenderer.invoke('file:getInfo', path),
  // list videos imported into the app
  getVideoFiles: () => ipcRenderer.invoke('get-video-files'),
  // import (copy) a video into app storage
  importVideo: (srcPath: string) => ipcRenderer.invoke('import-video', srcPath),
};

contextBridge.exposeInMainWorld('api', api);