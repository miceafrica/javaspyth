from flask import Flask, request, jsonify, send_from_directory
import subprocess
import os
import asyncio
from threading import Thread

# Import Playwright for advanced scraping
from playwright.async_api import async_playwright

# The Flask app is initialized correctly to serve the frontend
app = Flask(__name__, static_folder='../frontend', static_url_path='/')

# This route serves your index.html file
@app.route('/')
def serve_frontend():
    return send_from_directory(app.static_folder, 'index.html')

# This is the API endpoint for executing code
@app.route('/execute', methods=['POST'])
def execute_code():
    data = request.get_json()
    language = data.get('language')
    code = data.get('code')

    if not language or not code:
        return jsonify({'error': 'Language and code are required.'}), 400

    if language not in ['python', 'javascript']:
        return jsonify({'error': 'Unsupported language.'}), 400

    try:
        # Code execution logic remains the same
        if language == 'python':
            result = subprocess.run(
                ['python3', '-c', code],
                capture_output=True,
                text=True,
                timeout=50
            )
        elif language == 'javascript':
            result = subprocess.run(
                ['node', '-e', code],
                capture_output=True,
                text=True,
                timeout=50
            )

        # This is the logic for successful code execution
        if result.returncode == 0:
            return jsonify({'output': result.stdout})
        # This is the corrected logic for when the user's code has an error
        else:
            # FIX #1: Combine stdout and stderr to show all output before the error
            full_error_output = result.stdout + result.stderr
            
            # FIX #2: Return an HTTP 400 error status so the frontend can detect it
            return jsonify({'error': full_error_output}), 400

    except subprocess.TimeoutExpired:
        return jsonify({'error': 'Execution timed out after 5 seconds.'}), 408
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Helper function to run async Playwright code in a thread
def run_async_playwright(coro):
    return asyncio.run(coro)

# New API endpoint for Playwright scraping
@app.route('/scrape/playwright', methods=['POST'])
def scrape_playwright():
    data = request.get_json()
    url = data.get('url')
    selector = data.get('selector')

    if not url or not selector:
        return jsonify({'error': 'URL and selector are required.'}), 400

    try:
        # Run Playwright scraping in a separate thread to avoid blocking
        result = {}

        def scrape():
            async def run():
                async with async_playwright() as p:
                    browser = await p.chromium.launch()
                    page = await browser.new_page()
                    await page.goto(url)
                    content = await page.text_content(selector)
                    await browser.close()
                    return content

            content = asyncio.run(run())
            result['content'] = content

        thread = Thread(target=scrape)
        thread.start()
        thread.join()

        if 'content' in result:
            return jsonify({'content': result['content']})
        else:
            return jsonify({'error': 'Failed to scrape content.'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# This is the necessary block to run the app
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
