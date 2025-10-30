import { contextBridge, ipcRenderer } from 'electron';
import type { RendererAPI, OpenDialogResult } from '../common/types';

const api: RendererAPI = {
  ping: () => ipcRenderer.invoke('ping'),
  pickVideo: (): Promise<OpenDialogResult> => ipcRenderer.invoke('dialog:openVideo'),
  pickDirectory: (): Promise<OpenDialogResult> => ipcRenderer.invoke('dialog:openDirectory'),
  config: {
    read: () => ipcRenderer.invoke('config:read'),
    write: (data) => ipcRenderer.invoke('config:write', data)
  }
};

contextBridge.exposeInMainWorld('api', api);