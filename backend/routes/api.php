<?php

use Illuminate\\Support\\Facades\\Route;

Route::prefix('v1')->group(function () {
    Route::get('/health', fn () => response()->json([
        'data' => [
            'status' => 'ok',
            'service' => 'laxmannepal-api',
            'version' => 'v1',
        ],
    ]));

    Route::get('/articles', fn () => response()->json(['data' => [], 'meta' => ['page' => 1, 'limit' => 20, 'total' => 0]]));
    Route::get('/products', fn () => response()->json(['data' => [], 'meta' => ['page' => 1, 'limit' => 20, 'total' => 0]]));
    Route::get('/tools', fn () => response()->json(['data' => [], 'meta' => ['page' => 1, 'limit' => 20, 'total' => 0]]));
    Route::get('/youtube/channels', fn () => response()->json(['data' => [], 'meta' => ['page' => 1, 'limit' => 20, 'total' => 0]]));
});
