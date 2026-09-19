<?php

namespace App\\Models;

use Illuminate\\Database\\Eloquent\\Model;

class Article extends Model
{
    protected $fillable = [
        'author_id',
        'type',
        'status',
        'title',
        'slug',
        'excerpt',
        'cover_media_id',
        'published_at',
    ];

    protected $casts = [
        'published_at' => 'datetime',
    ];
}
