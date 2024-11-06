// PDF viewer enabled
// Bypasses `pdfIsDisabled` test in creepsjs's 'Like Headless' sections
Object.defineProperty(navigator, 'pdfViewerEnabled', {
    get: () => true,
});