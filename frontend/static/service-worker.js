self.addEventListener('install', function(e) {
    e.waitUntil(
        caches.open('your-cache-name').then(function(cache) {
            return cache.addAll([]);
        })
    );
});
