let baseURL = "https://github.com/wishrito/"
function redirect(varName) {
    if (varName) {
        window.open(baseURL + varName)
    } else {
        window.open(baseURL)
    }
}