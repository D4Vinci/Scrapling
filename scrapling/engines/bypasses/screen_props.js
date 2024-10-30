const windowScreenProps = {
    // Dimensions
    innerHeight: 0,
    innerWidth: 0,
    outerHeight: 754,
    outerWidth: 1313,

    // Position
    screenX: 19,
    pageXOffset: 0,
    pageYOffset: 0,

    // Display
    devicePixelRatio: 2
};

try {
    for (const [prop, value] of Object.entries(windowScreenProps)) {
        if (value > 0) {
            // The 0 values are introduced by collecting in the hidden iframe.
            // They are document sizes anyway so no need to test them or inject them.
            window[prop] = value;
        }
    }
} catch (e) {
    console.warn(e);
};