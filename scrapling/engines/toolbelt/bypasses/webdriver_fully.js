// Create a function that looks like a native getter
const nativeGetter = function get webdriver() {
    return false;
};

// Copy over native function properties
Object.defineProperties(nativeGetter, {
    name: { value: 'get webdriver', configurable: true },
    length: { value: 0, configurable: true },
    toString: {
        value: function() {
            return `function get webdriver() { [native code] }`;
        },
        configurable: true
    }
});

// Make it look native
Object.setPrototypeOf(nativeGetter, Function.prototype);

// Apply the modified descriptor
Object.defineProperty(Navigator.prototype, 'webdriver', {
    get: nativeGetter,
    set: undefined,
    enumerable: true,
    configurable: true
});