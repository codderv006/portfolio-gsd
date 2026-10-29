# vedant-builds

Source for **[vedant-builds.vercel.app](https://vedant-builds.vercel.app)**: the portfolio of Vedant Pawar, plus per-company application pages.

- `/` portfolio (static HTML, no build step). Formal + quirky mode, role lens (`?for=pm|pe|data|fs|fo`), favourites slideshow.
- `/nue`, `/dotstore`, `/smc` application pages (noindexed).
- `/llms.txt`, `/llms-full.txt` LLM-friendly profile. JSON-LD in the page head.
- `favorites.js` lists the photos in `assets/favorites/web/`, in display order.

Deployed on Vercel; every push to `main` goes live.
