# Page snapshot

```yaml
- generic [ref=e3]:
  - generic [ref=e4]: "[plugin:vite:import-analysis] Failed to resolve import \"./components/SocketStatus\" from \"src/App.jsx\". Does the file exist?"
  - generic [ref=e5]: /app/src/App.jsx:10:25
  - generic [ref=e6]: 25 | import Header from "./components/Header"; 26 | import NotificationSystem from "./components/NotificationSystem"; 27 | import SocketStatus from "./components/SocketStatus"; | ^ 28 | import HomePage from "./pages/HomePage"; 29 | import Home from "./pages/Home";
  - generic [ref=e7]: at TransformPluginContext._formatLog (file:///app/node_modules/vite/dist/node/chunks/dep-M_KD0XSK.js:31527:43) at TransformPluginContext.error (file:///app/node_modules/vite/dist/node/chunks/dep-M_KD0XSK.js:31524:14) at normalizeUrl (file:///app/node_modules/vite/dist/node/chunks/dep-M_KD0XSK.js:29996:18) at process.processTicksAndRejections (node:internal/process/task_queues:95:5) at async file:///app/node_modules/vite/dist/node/chunks/dep-M_KD0XSK.js:30054:32 at async Promise.all (index 12) at async TransformPluginContext.transform (file:///app/node_modules/vite/dist/node/chunks/dep-M_KD0XSK.js:30022:4) at async EnvironmentPluginContainer.transform (file:///app/node_modules/vite/dist/node/chunks/dep-M_KD0XSK.js:31325:14) at async loadAndTransform (file:///app/node_modules/vite/dist/node/chunks/dep-M_KD0XSK.js:26407:26) at async viteTransformMiddleware (file:///app/node_modules/vite/dist/node/chunks/dep-M_KD0XSK.js:27492:20)
  - generic [ref=e8]:
    - text: Click outside, press Esc key, or fix the code to dismiss.
    - text: You can also disable this overlay by setting
    - code [ref=e9]: server.hmr.overlay
    - text: to
    - code [ref=e10]: "false"
    - text: in
    - code [ref=e11]: vite.config.js
    - text: .
```