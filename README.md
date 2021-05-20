# VISstarter-vue

Rapid visualization starter kit for VIS &amp; ML projects.

## Setup
1. `./setup_new.sh <MyProjectname>`

    <details>
    <summary>or <b>MANUALLY</b>...</summary>
    Change the `vis-starter` text (and, if needed, author/description), in the following files:

    - `environment.yml`
    - `client/package.json`
    - `setup.py`
    - `client/index.html`
    </details>

2. Replace LICENSE as desired.

3. Modify `backend/server/main.py` file for desired routes. API types are typically stored in `backend/server/api.py`
### Backend

From the root directory:

```
conda env create -f environment.yml
conda activate <MyProjectName>
pip install -e .
```

Run the backend in development mode:

```
uvicorn backend.server:app --reload
```

<details>
<summary><b>For production (single worker)</b></summary>

```
uvicorn backend.server:app
```

</details>

<details>
<summary><b>For production (multiple workers)</b></summary>

```
gunicorn -w 4 -k uvicorn.workers.UvicornWorker backend.server:app
```

where `4` is the number of workers desired.
</details>

<details>
<summary><b>Testing</b></summary>

```
pytest tests
```

All tests are stored in `tests`.

</details>

### Frontend

We like [`pnpm`](https://pnpm.io/installation) but `npm` works just as well. We also like [`Vite`](https://vitejs.dev/) for its rapid hot module reloading and pleasant dev experience. This repository uses [`Vue`](https://vuejs.org/) as a reactive framework.

From the root directory:

```
cd client
pnpm install --save-dev
pnpm run dev
```

If you want to hit the backend routes, make sure to also run the `uvicorn backend.server:app` command from the project root.

<details>
<summary><b>Serve with Vite</b></summary>

```
pnpm run serve
```

</details>

<details>
<summary><b>Serve with this repo's FastAPI server</b></summary>

```
pnpm run build:backend
```

All artifacts are stored in the `client/dist` directory with the appropriate basepath.
</details>

<details>
<summary><b>Serve with external tooling</b></summary>

```
pnpm run build
```

All artifacts are stored in the `client/dist` directory.
</details>

## Notes

- Check the endpoints by visiting `<localhost>:<port>/docs`