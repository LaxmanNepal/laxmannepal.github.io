<?php

namespace App\\Models;

use Illuminate\\Database\\Eloquent\\Model;

class Product extends Model
{
    protected $fillable = [
        'brand_id',
        'category_id',
        'name',
        'slug',
        'model',
        'description',
        'release_date',
        'status',
    ];

    protected $casts = [
        'release_date' => 'date',
    ];
}
