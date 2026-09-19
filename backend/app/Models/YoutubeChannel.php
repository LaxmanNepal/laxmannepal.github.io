<?php

namespace App\\Models;

use Illuminate\\Database\\Eloquent\\Model;

class YoutubeChannel extends Model
{
    protected $fillable = [
        'platform_id',
        'handle',
        'name',
        'slug',
        'url',
        'avatar_url',
        'subscribers',
    ];

    protected $casts = [
        'subscribers' => 'integer',
    ];
}
