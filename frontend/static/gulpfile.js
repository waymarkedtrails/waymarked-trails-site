var gulp = require('gulp'),
    sass = require('gulp-sass'),
    sourcemaps = require('gulp-sourcemaps'),
    autoprefixer = require('gulp-autoprefixer'),
    gulpif = require('gulp-if'),
    webpack = require('webpack2-stream-watch'),
    uglify = require('gulp-uglify'),
    concat = require('gulp-concat'),
    merge = require('merge-stream');

var argv = require('yargs').argv;
var isProduction = (argv.production === undefined) ? false : true;

gulp.task('default', ['css', 'js'], function () {
});

gulp.task('css', function () {
    return gulp
      .src('scss/**/*.scss')
      .pipe(gulpif(!isProduction, sourcemaps.init()))
      .pipe(sass({
          errLogToConsole: true,
          outputStyle: isProduction ? 'compressed' : 'expanded'
        }).on('error', sass.logError))
      .pipe(gulpif(!isProduction, sourcemaps.write()))
      .pipe(autoprefixer())
      .pipe(gulp.dest('css/'));
});

gulp.task('js', function () {
    var vendor = gulp.src('js/vendor.js')
      .pipe(webpack({
          output: {
              filename: 'vendorBase.js'
          }
      }))
      .pipe(gulp.dest('packed/'));

    var concatFiles = gulp.src([
        'packed/vendorBase.js',
        'contrib/jqm.page.params.js',
        'node_modules/jquery-mobile/dist/jquery.mobile.js'
      ])
      .pipe(concat('vendor.js'))
      .pipe(gulpif(isProduction, uglify()))
      .pipe(gulp.dest('packed/'));

    return merge(vendor, concatFiles);
});
