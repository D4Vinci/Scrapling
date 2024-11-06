// Bypasses `notificationIsDenied` test in creepsjs's 'Like Headless' sections
const isSecure = document.location.protocol.startsWith('https')
if (isSecure){
    Object.defineProperty(Notification, 'permission', {get: () => 'default'})
}