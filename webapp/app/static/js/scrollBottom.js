var scrollingElement = (document.scrollingElement || document.body);
function scrollToBottom () {
   scrollingElement.scrollTop = scrollingElement.scrollHeight;
}
