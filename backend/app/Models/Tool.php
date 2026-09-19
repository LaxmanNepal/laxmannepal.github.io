<?php

namespace App\\Models;

use Illuminate\\Database\\Eloquent\\Model;

class Tool extends Model
{
    protected $fillable = [
        'category_id',
        'name',
        'slug',
        'description',
        'url',
        'icon_media_id',
        'status',
    ];
}
