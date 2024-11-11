if(navigator.plugins.length == 0){
    Object.defineProperty(navigator, 'plugins', {
        get: () => {
            const PDFViewerPlugin = Object.create(Plugin.prototype, {
                description: { value: 'Portable Document Format', enumerable: false },
                filename: { value: 'internal-pdf-viewer', enumerable: false },
                name: { value: 'PDF Viewer', enumerable: false },
            });
            const ChromePDFViewer = Object.create(Plugin.prototype, {
                description: { value: 'Portable Document Format', enumerable: false },
                filename: { value: 'internal-pdf-viewer', enumerable: false },
                name: { value: 'Chrome PDF Viewer', enumerable: false },
            });
            const ChromiumPDFViewer = Object.create(Plugin.prototype, {
                description: { value: 'Portable Document Format', enumerable: false },
                filename: { value: 'internal-pdf-viewer', enumerable: false },
                name: { value: 'Chromium PDF Viewer', enumerable: false },
            });
            const EdgePDFViewer = Object.create(Plugin.prototype, {
                description: { value: 'Portable Document Format', enumerable: false },
                filename: { value: 'internal-pdf-viewer', enumerable: false },
                name: { value: 'Microsoft Edge PDF Viewer', enumerable: false },
            });
            const WebKitPDFPlugin = Object.create(Plugin.prototype, {
                description: { value: 'Portable Document Format', enumerable: false },
                filename: { value: 'internal-pdf-viewer', enumerable: false },
                name: { value: 'WebKit built-in PDF', enumerable: false },
            });

            return Object.create(PluginArray.prototype, {
                length: { value: 5 },
                0: { value: PDFViewerPlugin },
                1: { value: ChromePDFViewer },
                2: { value: ChromiumPDFViewer },
                3: { value: EdgePDFViewer },
                4: { value: WebKitPDFPlugin },
            });
        },
    });
}