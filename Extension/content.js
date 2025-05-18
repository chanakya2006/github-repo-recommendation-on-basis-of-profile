async function fetching(username) {
    try{
        const response = await fetch(`http://127.0.0.1:5000/api?name=${encodeURIComponent(username)}`);
    
        // Check if the request was successful
        if (!response.ok) {
          throw new Error(`API request failed with status: ${response.status}`);
        }

        // Parse the JSON response
        const data = await response.json();

        return data;
    } catch (error) {
        console.error('Error fetching repository data:', error);
        // Display error message to the user
        return null;
  }
}

function injectHTML(data) {
  const targetDiv = document.querySelector('div[data-hpc]');
  if (targetDiv) {
    var base_html = `<article data-view-component="true" class="d-flex flex-column width-full py-3">
  <header data-view-component="true" class="d-flex flex-items-center flex-justify-between">
    <div data-view-component="true" class="d-flex flex-items-center">
      <span style="background-color: var(--bgColor-neutral-muted, var(--color-scale-gray-2));" data-view-component="true" class="circle d-inline-flex mr-2 p-2">
        <svg aria-hidden="true" height="16" viewBox="0 0 16 16" version="1.1" width="16" data-view-component="true" class="octicon octicon-north-star color-fg-subtle">
    <path d="M8.5.75a.75.75 0 0 0-1.5 0v5.19L4.391 3.33a.75.75 0 1 0-1.06 1.061L5.939 7H.75a.75.75 0 0 0 0 1.5h5.19l-2.61 2.609a.75.75 0 1 0 1.061 1.06L7 9.561v5.189a.75.75 0 0 0 1.5 0V9.56l2.609 2.61a.75.75 0 1 0 1.06-1.061L9.561 8.5h5.189a.75.75 0 0 0 0-1.5H9.56l2.61-2.609a.75.75 0 0 0-1.061-1.06L8.5 5.939V.75Z"></path>
</svg>
</span>      <h3 data-view-component="true" class="color-fg-muted f5 text-normal">Recommendations</h3>
</div>    
</header>  <ul class="d-flex flex-wrap mt-2 gutter-sm-condensed" style="list-style-type: none;">`
for (const key in data) {
  if (data.hasOwnProperty(key)) {
    base_html += `<li class="col-sm-12 col-md-6 mb-3">
        <a aria-describedby="c7e876cc-3916-4516-88ad-8bd792b8bcdc" data-analytics-event="{&quot;category&quot;:&quot;dashboard-feed-learn-component&quot;,&quot;action&quot;:&quot;click.introduction-to-github&quot;,&quot;label&quot;:&quot;target:${data[key]['url']}}" href="${data[key]['url']}" data-view-component="true" class="Link d-flex flex-column border rounded-2 color-shadow-medium color-bg-overlay p-3 height-full"><span data-view-component="true" class="color-fg-accent text-bold">${data[key]['repo_name']}</span>
          </a>      </li>`
  }
}
base_html += `</ul>
</article>`
    targetDiv.innerHTML += base_html;
  } else {
    console.warn('Target div with [data-hpc] not found.');
  }
}

async function extractGitHubUsername() {
    var temp;
  const metaTag = document.querySelector('meta[name="octolytics-actor-login"]');
    if (metaTag) {
      temp = metaTag.getAttribute('content');
      console.log(temp);
    } else {
      console.log("Meta tag not found.");
    }
    const a = await fetching(temp);
    console.log(a)
    injectHTML(a)
}

// Run when page loads
window.addEventListener('load', extractGitHubUsername);

// Also run when URL changes without page refresh (GitHub is a SPA)
let lastUrl = location.href;
new MutationObserver(() => {
  const url = location.href;
  if (url !== lastUrl) {
    lastUrl = url;
    extractGitHubUsername();
  }
}).observe(document, {subtree: true, childList: true});