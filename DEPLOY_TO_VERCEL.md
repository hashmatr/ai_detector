# Deploying to Vercel (The Easy Way)

Since your backend is on an IP address (`http://51.21.253.28`), we need to configure Vercel to "proxy" requests to it. This gives you a nice domain name (HTTPS) and prevents security errors.

I have already configured the `vercel.json` file to handle this proxying automatically.

## Deployment Steps

1.  **Open Terminal**:
    Open the terminal in VS Code if it's not already open.

2.  **Navigate to Frontend**:
    ```bash
    cd Frontend
    ```

3.  **Run Vercel Deploy**:
    ```bash
    vercel --prod
    ```
    - Follow the prompts (Select scope, default Project Name, etc.).
    - **IMPORTANT**: When asked about "Environment Variables", you do **NOT** need to add any. Leave them default.
    - Why? Because we hardcoded your IP into `vercel.json` to make the proxying work seamlessly.

## How it Works
-   User visits: `https://your-project.vercel.app` (Secure HTTPS)
-   Frontend calls: `https://your-project.vercel.app/predict`
-   Vercel (server-side) forwards to: `http://51.21.253.28/predict`
-   Browser is happy (No Mixed Content warnings).
-   Backend is happy.

## Updating the Backend IP
If your AWS IP changes in the future, just edit `Frontend/vercel.json` and replace `51.21.253.28` with your new IP, then run `vercel --prod` again.
