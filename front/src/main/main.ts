import { app, BrowserWindow, ipcMain, dialog } from 'electron';
import path from 'path';
import fs from 'fs/promises';

const isDev = !app.isPackaged;
let win: BrowserWindow | null = null;

function getConfigPath() {
  const dir = path.join(app.getPath('userData'), 'videolingo');
  return { dir, file: path.join(dir, 'config.json') };
}

async function ensureDir(p: string) {
  await fs.mkdir(p, { recursive: true }).catch(() => {});
}

function createWindow() {
  win = new BrowserWindow({
    width: 1100, height: 700,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true, nodeIntegration: false
    }
  });

  if (isDev) {
    win.loadURL('http://localhost:5173');
    win.webContents.openDevTools();
  } else {
    win.loadFile(path.join(__dirname, '../renderer/index.html'));
  }

  win.on('closed', () => (win = null));
}

app.whenReady().then(() => {
  createWindow();

  ipcMain.handle('ping', () => 'pong');

  ipcMain.handle('dialog:openVideo', async () => {
    const res = await dialog.showOpenDialog(win!, {
      title: '选择视频文件',
      properties: ['openFile'],
      filters: [
        { name: 'Video', extensions: ['mp4','mkv','mov','webm','avi'] },
        { name: 'All Files', extensions: ['*'] }
      ]
    });
    return { canceled: res.canceled, filePaths: res.filePaths };
  });

  ipcMain.handle('dialog:openDirectory', async () => {
    const res = await dialog.showOpenDialog(win!, {
      title: '选择目录',
      properties: ['openDirectory', 'createDirectory']
    });
    return { canceled: res.canceled, filePaths: res.filePaths };
  });

  ipcMain.handle('config:read', async () => {
    const { dir, file } = getConfigPath();
    await ensureDir(dir);
    try {
      const buf = await fs.readFile(file, 'utf-8');
      return JSON.parse(buf);
    } catch {
      return null;
    }
  });

  ipcMain.handle('config:write', async (_e, data: Record<string, any>) => {
    const { dir, file } = getConfigPath();
    await ensureDir(dir);
    try {
      await fs.writeFile(file, JSON.stringify(data ?? {}, null, 2), 'utf-8');
      return true;
    } catch {
      return false;
    }
  });

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});