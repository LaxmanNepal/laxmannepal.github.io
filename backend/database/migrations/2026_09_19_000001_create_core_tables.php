<?php

use Illuminate\\Database\\Migrations\\Migration;
use Illuminate\\Database\\Schema\\Blueprint;
use Illuminate\\Support\\Facades\\Schema;

return new class extends Migration {
    public function up(): void
    {
        Schema::create('authors', function (Blueprint $table) {
            $table->id(); $table->string('name'); $table->string('slug')->unique();
            $table->text('bio')->nullable(); $table->string('avatar_url')->nullable(); $table->timestamps();
        });
        Schema::create('categories', function (Blueprint $table) {
            $table->id(); $table->foreignId('parent_id')->nullable()->constrained('categories')->nullOnDelete();
            $table->string('name'); $table->string('slug')->unique(); $table->text('description')->nullable(); $table->timestamps();
        });
        Schema::create('brands', function (Blueprint $table) {
            $table->id(); $table->string('name'); $table->string('slug')->unique();
            $table->string('logo_media_id')->nullable(); $table->string('website_url')->nullable(); $table->timestamps();
        });
        Schema::create('products', function (Blueprint $table) {
            $table->id(); $table->foreignId('brand_id')->nullable()->constrained()->nullOnDelete();
            $table->foreignId('category_id')->nullable()->constrained('categories')->nullOnDelete();
            $table->string('name'); $table->string('slug')->unique(); $table->string('model')->nullable();
            $table->text('description')->nullable(); $table->date('release_date')->nullable();
            $table->string('status')->default('draft'); $table->timestamps(); $table->index(['brand_id','category_id']);
        });
        Schema::create('articles', function (Blueprint $table) {
            $table->id(); $table->foreignId('author_id')->nullable()->constrained()->nullOnDelete();
            $table->string('type')->default('news'); $table->string('status')->default('draft');
            $table->string('title'); $table->string('slug')->unique(); $table->text('excerpt')->nullable();
            $table->unsignedBigInteger('cover_media_id')->nullable(); $table->timestampTz('published_at')->nullable();
            $table->timestamps(); $table->index(['status','published_at']);
        });
        Schema::create('tools', function (Blueprint $table) {
            $table->id(); $table->foreignId('category_id')->nullable()->constrained('categories')->nullOnDelete();
            $table->string('name'); $table->string('slug')->unique(); $table->text('description')->nullable();
            $table->string('url'); $table->string('icon_media_id')->nullable(); $table->string('status')->default('active'); $table->timestamps();
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('tools');
        Schema::dropIfExists('articles');
        Schema::dropIfExists('products');
        Schema::dropIfExists('brands');
        Schema::dropIfExists('categories');
        Schema::dropIfExists('authors');
    }
};
