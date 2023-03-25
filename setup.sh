mkdir -p ~/.streamlit/

echo "\
[general]\n\
email = \"alex@rocksolidrevenue.com\"\n\
" > ~/.streamlit/credentials.toml

echo "\
[server]\n\
headless = true\n\
enableXsrfProtection=false
enableCORS=false\n\
port = $PORT\n\
" > ~/.streamlit/config.toml
