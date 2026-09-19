<?php

use Illuminate\\Database\\Migrations\\Migration;
use Illuminate\\Database\\Schema\\Blueprint;
use Illuminate\\Support\\Facades\\Schema;

return new class extends Migration {
    public function up(): void
    {
        Schema::create('youtube_channels', function (Blueprint $table) {
            $table->id(); $table->string('platform_id')->unique(); $table->string('handle')->nullable();
            $table->string('name'); $table->string('slug')->unique(); $table->string('url');
            $table->string('avatar_url')->nullable(); $table->unsignedBigInteger('subscribers')->default(0); $table->timestamps();
        });
        Schema::create('youtube_videos', function (Blueprint $table) {
            $table->id(); $table->foreignId('channel_id')->constrained('youtube_channels')->cascadeOnDelete();
            $table->string('platform_id')->unique(); $table->string('title'); $table->string('slug');
            $table->string('url'); $table->timestampTz('published_at')->nullable();
            $table->unsignedInteger('duration_seconds')->nullable(); $table->string('thumbnail_url')->nullable(); $table->timestamps();
            $table->index(['channel_id','published_at']);
        });
        Schema::create('youtube_snapshots', function (Blueprint $table) {
            $table->id(); $table->foreignId('channel_id')->constrained('youtube_channels')->cascadeOnDelete();
            $table->timestampTz('captured_at'); $table->unsignedBigInteger('subscribers')->default(0);
            $table->unsignedBigInteger('views')->default(0); $table->unsignedBigInteger('video_count')->default(0);
            $table->index(['channel_id','captured_at']);
        });
        Schema::create('youtube_video_snapshots', function (Blueprint $table) {
            $table->id(); $table->foreignId('video_id')->constrained('youtube_videos')->cascadeOnDelete();
            $table->timestampTz('captured_at'); $table->unsignedBigInteger('views')->default(0);
            $table->unsignedBigInteger('likes')->default(0); $table->unsignedBigInteger('comments')->default(0);
            $table->index(['video_id','captured_at']);
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('youtube_video_snapshots');
        Schema::dropIfExists('youtube_snapshots');
        Schema::dropIfExists('youtube_videos');
        Schema::dropIfExists('youtube_channels');
    }
};
