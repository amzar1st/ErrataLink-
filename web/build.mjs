import { build } from 'esbuild';
import { copyFile, mkdir } from 'node:fs/promises';

await mkdir('dist', { recursive: true });
await Promise.all(['index.html', 'style.css'].map(file => copyFile('web/' + file, 'dist/' + file)));
await build({ entryPoints: ['web/app.mjs'], outfile: 'dist/app.js', bundle: true, minify: true, format: 'esm', target: 'es2022' });
