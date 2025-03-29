from evaluator import *

question = """
Create a Rust CLI program that takes an asciinema dump and creates a plain text dump of the terminal state each frame, using the same the frame choice algorithm that agg uses.  Then the frames are output to stdout, of the format:

```
FRAME0_LINE0 (COL characters wide)
FRAME0_LINE1
...
FRAME0_LINEN (ROW characters tall)
----
FRAME1_LINE0
...
---- (trailing delimiter)
```

For example, suppose an asciinema dump is of a 2x2 window counting down from three.  Then we output:

```
3 
  
----
2 
  
----
1 
  
----
0 
  
----
```

Note that lines are padded out to the full column length with spaces.

Use avt as your terminal emulator.  You will compile with the following Cargo.toml attached below.
I've also attached the agg source code as reference.
"""

cargo = r"""
[package]
name = "agg_to_text"
version = "0.1.0"
edition = "2024"

[dependencies]
avt = "0.15.1"
anyhow = "1.0"
clap = { version = "4.4", features = ["derive"] }
serde = { version = "1.0", features = ["derive"] }
serde_json = "1.0"
"""

context = r"""
This file is a merged representation of a subset of the codebase, containing files not matching ignore patterns, combined into a single document by Repomix. The content has been processed where security check has been disabled.

<file_summary>
This section contains a summary of this file.

<purpose>
This file contains a packed representation of the entire repository's contents.
It is designed to be easily consumable by AI systems for analysis, code review,
or other automated processes.
</purpose>

<file_format>
The content is organized as follows:
1. This summary section
2. Repository information
3. Directory structure
4. Repository files, each consisting of:
  - File path as an attribute
  - Full contents of the file
</file_format>

<usage_guidelines>
- This file should be treated as read-only. Any changes should be made to the
  original repository files, not this packed version.
- When processing this file, use the file path to distinguish
  between different files in the repository.
- Be aware that this file may contain sensitive information. Handle it with
  the same level of security as you would the original repository.
</usage_guidelines>

<notes>
- Some files may have been excluded based on .gitignore rules and Repomix's configuration
- Binary files are not included in this packed representation. Please refer to the Repository Structure section for a complete list of file paths, including binary files
- Files matching these patterns are excluded: **/*.cast, LICENSE, .github/*, src/renderer/*
- Files matching patterns in .gitignore are excluded
- Files matching default ignore patterns are excluded
- Security check has been disabled - content may contain sensitive information
</notes>

<additional_info>

</additional_info>

</file_summary>

<directory_structure>
.github/
  ISSUE_TEMPLATE/
    bug_report.md
    config.yml
  workflows/
    build_nix.yml
    ci.yml
    publish.yml
    release.yml
src/
  asciicast.rs
  events.rs
  fonts.rs
  lib.rs
  main.rs
  renderer.rs
  theme.rs
  vt.rs
.dockerignore
.gitignore
Cargo.toml
default.nix
Dockerfile
flake.lock
flake.nix
README.md
shell.nix
</directory_structure>

<files>
This section contains the contents of the repository's files.

<file path=".github/ISSUE_TEMPLATE/bug_report.md">
---
name: Bug report
about: Create a report to help improve agg
title: ''
labels: ''
assignees: ''

---

To make life of the project maintainers easier please submit bug reports only.

This is a bug tracker for asciinema gif generator (aka agg).
If your issue seems to be with another component (cli recorder, js player, server) then open an issue in the related repository.

Ideas, feature requests, help requests, questions and general discussions should be discussed on the forum: https://discourse.asciinema.org

If you think you've found a bug or regression, go ahead, delete this message, then fill in the details below.

-----

**Describe the bug**
A clear and concise description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. ...
2. ...
3. ...
4. See error

**Expected behavior**
A clear and concise description of what you expected to happen.

**Versions:**
 - OS: [e.g. macOS 12.6, Ubuntu 23.04]
 - agg: [e.g. 1.4.1]

**Additional context**
Add any other context about the problem here.
</file>

<file path=".github/ISSUE_TEMPLATE/config.yml">
blank_issues_enabled: false
contact_links:
  - name: Forum
    url: https://discourse.asciinema.org/
    about: Ideas, feature requests, help requests, questions and general discussions should be posted here.
  - name: GitHub discussions
    url: https://github.com/orgs/asciinema/discussions
    about: Ideas, feature requests, help requests, questions and general discussions should be posted here.
</file>

<file path=".github/workflows/build_nix.yml">
name: "Build legacy Nix package on Ubuntu"

on:
  push:
    branches: ["main"]
  pull_request:
    branches: ["main"]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: cachix/install-nix-action@v20
      - name: Building package
        run: nix-build . -A defaultPackage.x86_64-linux
</file>

<file path=".github/workflows/ci.yml">
name: CI

on:
  push:
    branches: ["main"]
  pull_request:
    branches: ["main"]

env:
  CARGO_TERM_COLOR: always

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Install Rust toolchain
        uses: actions-rs/toolchain@v1
        with:
          profile: minimal
          toolchain: stable
          components: rustfmt, clippy
          override: true

      - name: Build
        run: cargo build --verbose

      - name: Run tests
        run: cargo test --verbose

      - name: Check formatting
        run: cargo fmt --check

      - name: Lint with clippy
        run: cargo clippy
</file>

<file path=".github/workflows/publish.yml">
name: Publish

on:
  push:
    branches:
      - main
    tags:
      - "v*"

env:
  IMAGE_NAME: agg

jobs:
  publish:
    runs-on: ubuntu-22.04
    permissions:
      packages: write
      contents: read

    steps:
      - uses: actions/checkout@v4

      - name: Build image
        run: docker build . --file Dockerfile --tag $IMAGE_NAME --label "runnumber=${GITHUB_RUN_ID}"

      - name: Log in to registry
        run: echo "${{ secrets.GITHUB_TOKEN }}" | docker login ghcr.io -u $ --password-stdin

      - name: Push image
        run: |
          IMAGE_ID=ghcr.io/${{ github.repository_owner }}/$IMAGE_NAME

          # Change all uppercase to lowercase
          IMAGE_ID=$(echo $IMAGE_ID | tr '[A-Z]' '[a-z]')
          # Strip git ref prefix from version
          VERSION=$(echo "${{ github.ref }}" | sed -e 's,.*/\(.*\),\1,')
          # Strip "v" prefix from tag name
          [[ "${{ github.ref }}" == "refs/tags/"* ]] && VERSION=$(echo $VERSION | sed -e 's/^v//')
          # Use Docker `latest` tag convention
          [ "$VERSION" == "main" ] && VERSION=latest
          echo IMAGE_ID=$IMAGE_ID
          echo VERSION=$VERSION
          docker tag $IMAGE_NAME $IMAGE_ID:$VERSION
          docker push $IMAGE_ID:$VERSION
</file>

<file path=".github/workflows/release.yml">
name: Release

on:
  push:
    tags:
      - "v*.*.*"

jobs:
  publish:
    name: ${{ matrix.target }}
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        include:
          - os: ubuntu-latest
            target: x86_64-unknown-linux-gnu
            use-cross: false
            strip: strip

          - os: ubuntu-latest
            target: x86_64-unknown-linux-musl
            use-cross: false
            strip: strip

          - os: ubuntu-latest
            target: arm-unknown-linux-gnueabihf
            use-cross: true
            strip: arm-linux-gnueabihf-strip

          - os: ubuntu-latest
            target: aarch64-unknown-linux-gnu
            use-cross: true
            strip: aarch64-linux-gnu-strip

          - os: windows-latest
            target: x86_64-pc-windows-msvc
            use-cross: false
            binary_ext: ".exe"

          - os: macos-latest
            target: x86_64-apple-darwin
            use-cross: false
            strip: strip

          - os: macos-latest
            target: aarch64-apple-darwin
            use-cross: false
            strip: strip

    steps:
      - uses: actions/checkout@v3

      - name: Install Rust
        uses: actions-rs/toolchain@v1
        with:
          toolchain: stable
          profile: minimal
          override: true
          target: ${{ matrix.target }}

      - name: Install required dependencies
        shell: bash
        run: |
          if [[ ${{ matrix.target }} == x86_64-unknown-linux-musl ]]; then
              sudo apt-get update
              sudo apt-get install -y musl-tools
          fi
          if [[ ${{ matrix.target }} == aarch64-unknown-linux-gnu ]]; then
              sudo apt-get update
              sudo apt-get install -y binutils-aarch64-linux-gnu
          fi
          if [[ ${{ matrix.target }} == arm-unknown-linux-gnueabihf ]]; then
              sudo apt-get update
              sudo apt-get install -y binutils-arm-linux-gnueabihf
          fi

      - name: Build
        uses: actions-rs/cargo@v1
        with:
          use-cross: ${{ matrix.use-cross }}
          command: build
          args: --target ${{ matrix.target }} --release --locked

      - name: Strip binary
        if: matrix.strip
        run: ${{ matrix.strip }} target/${{ matrix.target }}/release/agg${{ matrix.binary_ext }}

      - name: Upload binaries to release
        uses: svenstaro/upload-release-action@v2
        with:
          repo_token: ${{ secrets.GITHUB_TOKEN }}
          file: target/${{ matrix.target }}/release/agg${{ matrix.binary_ext }}
          asset_name: agg-${{ matrix.target }}${{ matrix.binary_ext }}
          tag: ${{ github.ref }}
</file>

<file path="src/asciicast.rs">
use serde::Deserialize;
use std::fmt::Display;
use std::io::BufRead;

use crate::theme::Theme;

#[derive(Deserialize)]
pub struct V2Theme {
    fg: String,
    bg: String,
    palette: String,
}

#[derive(Deserialize)]
pub struct V2Header {
    pub width: usize,
    pub height: usize,
    pub idle_time_limit: Option<f64>,
    pub theme: Option<V2Theme>,
}

pub struct Header {
    pub terminal_size: (usize, usize),
    pub idle_time_limit: Option<f64>,
    pub theme: Option<Theme>,
}

#[derive(PartialEq, Eq, Debug)]
pub enum EventType {
    Output,
    Input,
    Other(char),
}

pub struct Event {
    pub time: f64,
    pub type_: EventType,
    pub data: String,
}

#[derive(Debug)]
pub enum Error {
    Io(std::io::Error),
    EmptyFile,
    InvalidEventTime,
    InvalidEventType(String),
    InvalidEventData,
    InvalidTheme,
    ParseJson(serde_json::Error),
}

impl TryInto<Header> for V2Header {
    type Error = Error;

    fn try_into(self) -> Result<Header, Self::Error> {
        let theme = match self.theme {
            Some(V2Theme { bg, fg, palette })
                if bg.len() == 7
                    && fg.len() == 7
                    && (palette.len() == 63 || palette.len() == 127) =>
            {
                let palette = palette
                    .split(':')
                    .map(|s| &s[1..])
                    .collect::<Vec<_>>()
                    .join(",");

                let theme = format!("{},{},{}", &bg[1..], &fg[1..], palette);

                Some(theme.parse().or(Err(Error::InvalidTheme))?)
            }

            Some(_) => return Err(Error::InvalidTheme),
            None => None,
        };

        Ok(Header {
            terminal_size: (self.width, self.height),
            idle_time_limit: self.idle_time_limit,
            theme,
        })
    }
}

impl Display for Error {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        std::fmt::Debug::fmt(&self, f)
    }
}

impl std::error::Error for Error {}

impl From<std::io::Error> for Error {
    fn from(err: std::io::Error) -> Self {
        Self::Io(err)
    }
}

impl From<serde_json::Error> for Error {
    fn from(err: serde_json::Error) -> Self {
        Self::ParseJson(err)
    }
}

pub fn open<R: BufRead>(
    reader: R,
) -> Result<(Header, impl Iterator<Item = Result<Event, Error>>), Error> {
    let mut lines = reader.lines();
    let first_line = lines.next().ok_or(Error::EmptyFile)??;
    let v2_header: V2Header = serde_json::from_str(&first_line)?;
    let header: Header = v2_header.try_into()?;

    let events = lines
        .filter(|line| line.as_ref().map_or(true, |l| !l.is_empty()))
        .map(|line| line.map(parse_event)?);

    Ok((header, events))
}

fn parse_event(line: String) -> Result<Event, Error> {
    let value: serde_json::Value = serde_json::from_str(&line)?;
    let time = value[0].as_f64().ok_or(Error::InvalidEventTime)?;

    let event_type = match value[1].as_str() {
        Some("o") => EventType::Output,
        Some("i") => EventType::Input,
        Some(s) if !s.is_empty() => EventType::Other(s.chars().next().unwrap()),
        Some(s) => return Err(Error::InvalidEventType(s.to_owned())),
        None => return Err(Error::InvalidEventType("".to_owned())),
    };

    let data = match value[2].as_str() {
        Some(data) => data.to_owned(),
        None => return Err(Error::InvalidEventData),
    };

    Ok(Event {
        time,
        type_: event_type,
        data,
    })
}

pub fn output(
    events: impl Iterator<Item = Result<Event, Error>>,
) -> impl Iterator<Item = (f64, String)> {
    events.filter_map(|e| match e {
        Ok(Event {
            type_: EventType::Output,
            time,
            data,
        }) => Some((time, data)),
        _ => None,
    })
}

#[cfg(test)]
mod tests {
    use std::{fs::File, io::BufReader};

    #[test]
    fn open() {
        let file = File::open("demo.cast").unwrap();
        let (header, events) = super::open(BufReader::new(file)).unwrap();

        let events = events
            .take(3)
            .collect::<Result<Vec<super::Event>, super::Error>>()
            .unwrap();

        assert_eq!(header.terminal_size, (89, 22));

        assert_eq!(events[0].time, 0.085923);
        assert_eq!(events[0].type_, super::EventType::Output);
        assert_eq!(events[0].data, "\u{1b}[?2004h");

        assert_eq!(events[1].time, 0.096545);
        assert_eq!(events[1].type_, super::EventType::Output);

        assert_eq!(events[2].time, 1.184101);
        assert_eq!(events[2].type_, super::EventType::Output);
        assert_eq!(events[2].data, "r\r\u{1b}[17C");
    }
}
</file>

<file path="src/events.rs">
type Event = (f64, String);

struct Batch<I>
where
    I: Iterator<Item = Event>,
{
    iter: I,
    prev_time: f64,
    prev_data: String,
    max_frame_time: f64,
}

impl<I: Iterator<Item = Event>> Iterator for Batch<I> {
    type Item = Event;

    fn next(&mut self) -> Option<Self::Item> {
        match self.iter.next() {
            Some((time, data)) => {
                if time - self.prev_time < self.max_frame_time {
                    self.prev_data.push_str(&data);

                    self.next()
                } else if !self.prev_data.is_empty() || self.prev_time == 0.0 {
                    let prev_time = self.prev_time;
                    self.prev_time = time;
                    let prev_data = std::mem::replace(&mut self.prev_data, data);

                    Some((prev_time, prev_data))
                } else {
                    self.prev_time = time;
                    self.prev_data = data;

                    self.next()
                }
            }

            None => {
                if !self.prev_data.is_empty() {
                    let prev_time = self.prev_time;
                    let prev_data = std::mem::replace(&mut self.prev_data, "".to_owned());

                    Some((prev_time, prev_data))
                } else {
                    None
                }
            }
        }
    }
}

pub fn batch(iter: impl Iterator<Item = Event>, fps_cap: u8) -> impl Iterator<Item = Event> {
    Batch {
        iter,
        prev_data: "".to_owned(),
        prev_time: 0.0,
        max_frame_time: 1.0 / (fps_cap as f64),
    }
}

pub fn accelerate(events: impl Iterator<Item = Event>, speed: f64) -> impl Iterator<Item = Event> {
    events.map(move |(time, data)| (time / speed, data))
}

pub fn limit_idle_time(
    events: impl Iterator<Item = Event>,
    limit: f64,
) -> impl Iterator<Item = Event> {
    let mut prev_time = 0.0;
    let mut offset = 0.0;

    events.map(move |(time, data)| {
        let delay = time - prev_time;
        let excess = delay - limit;

        if excess > 0.0 {
            offset += excess;
        }

        prev_time = time;

        (time - offset, data)
    })
}

#[cfg(test)]
mod tests {
    #[test]
    fn accelerate() {
        let stdout = [
            (0.0, "foo".to_owned()),
            (1.0, "bar".to_owned()),
            (2.0, "baz".to_owned()),
        ];

        let stdout = super::accelerate(stdout.into_iter(), 2.0).collect::<Vec<_>>();

        assert_eq!(&stdout[0], &(0.0, "foo".to_owned()));
        assert_eq!(&stdout[1], &(0.5, "bar".to_owned()));
        assert_eq!(&stdout[2], &(1.0, "baz".to_owned()));
    }

    #[test]
    fn batch() {
        let stdout = [
            (0.0, "foo".to_owned()),
            (1.0, "bar".to_owned()),
            (2.0, "baz".to_owned()),
        ];

        let stdout = super::batch(stdout.into_iter(), 30).collect::<Vec<_>>();

        assert_eq!(&stdout[0], &(0.0, "foo".to_owned()));
        assert_eq!(&stdout[1], &(1.0, "bar".to_owned()));
        assert_eq!(&stdout[2], &(2.0, "baz".to_owned()));

        let stdout = [
            (0.0, "foo".to_owned()),
            (0.033, "bar".to_owned()),
            (0.066, "baz".to_owned()),
            (1.0, "qux".to_owned()),
        ];

        let stdout = super::batch(stdout.into_iter(), 30).collect::<Vec<_>>();

        assert_eq!(&stdout[0], &(0.0, "foobar".to_owned()));
        assert_eq!(&stdout[1], &(0.066, "baz".to_owned()));
        assert_eq!(&stdout[2], &(1.0, "qux".to_owned()));

        let stdout = [
            (0.0, "".to_owned()),
            (1.0, "foo".to_owned()),
            (2.0, "bar".to_owned()),
        ];

        let stdout = super::batch(stdout.into_iter(), 30).collect::<Vec<_>>();

        assert_eq!(&stdout[0], &(0.0, "".to_owned()));
        assert_eq!(&stdout[1], &(1.0, "foo".to_owned()));
        assert_eq!(&stdout[2], &(2.0, "bar".to_owned()));
    }

    #[test]
    fn limit_idle_time() {
        let stdout = [
            (0.0, "foo".to_owned()),
            (1.0, "bar".to_owned()),
            (3.5, "baz".to_owned()),
            (4.0, "qux".to_owned()),
            (7.5, "quux".to_owned()),
        ];

        let stdout = super::limit_idle_time(stdout.into_iter(), 2.0).collect::<Vec<_>>();

        assert_eq!(&stdout[0], &(0.0, "foo".to_owned()));
        assert_eq!(&stdout[1], &(1.0, "bar".to_owned()));
        assert_eq!(&stdout[2], &(3.0, "baz".to_owned()));
        assert_eq!(&stdout[3], &(3.5, "qux".to_owned()));
        assert_eq!(&stdout[4], &(5.5, "quux".to_owned()));
    }
}
</file>

<file path="src/fonts.rs">
pub fn init(font_dirs: &[String], font_family: &str) -> Option<(fontdb::Database, Vec<String>)> {
    let mut font_db = fontdb::Database::new();
    font_db.load_system_fonts();

    for dir in font_dirs {
        font_db.load_fonts_dir(shellexpand::tilde(dir).to_string());
    }

    let mut families = font_family
        .split(',')
        .map(str::trim)
        .filter_map(|name| find_font_family(&font_db, name))
        .collect::<Vec<_>>();

    if families.is_empty() {
        None
    } else {
        for name in ["DejaVu Sans", "Noto Emoji"] {
            if let Some(name) = find_font_family(&font_db, name) {
                if !families.contains(&name) {
                    families.push(name);
                }
            }
        }

        Some((font_db, families))
    }
}

fn find_font_family(font_db: &fontdb::Database, name: &str) -> Option<String> {
    let family = fontdb::Family::Name(name);

    let query = fontdb::Query {
        families: &[family],
        weight: fontdb::Weight::NORMAL,
        stretch: fontdb::Stretch::Normal,
        style: fontdb::Style::Normal,
    };

    font_db.query(&query).and_then(|face_id| {
        let face_info = font_db.face(face_id).unwrap();
        face_info.families.first().map(|(family, _)| family.clone())
    })
}
</file>

<file path="src/lib.rs">
use anyhow::{anyhow, Result};
use clap::ArgEnum;
use log::info;
use std::fmt::{Debug, Display};
use std::io::{BufRead, Write};
use std::{iter, thread, time::Instant};
mod asciicast;
mod events;
mod fonts;
mod renderer;
mod theme;
mod vt;

pub const DEFAULT_FONT_FAMILY: &str =
    "JetBrains Mono,Fira Code,SF Mono,Menlo,Consolas,DejaVu Sans Mono,Liberation Mono";
pub const DEFAULT_FONT_SIZE: usize = 14;
pub const DEFAULT_FPS_CAP: u8 = 30;
pub const DEFAULT_LAST_FRAME_DURATION: f64 = 3.0;
pub const DEFAULT_LINE_HEIGHT: f64 = 1.4;
pub const DEFAULT_NO_LOOP: bool = false;
pub const DEFAULT_SPEED: f64 = 1.0;
pub const DEFAULT_IDLE_TIME_LIMIT: f64 = 5.0;

pub struct Config {
    pub cols: Option<usize>,
    pub font_dirs: Vec<String>,
    pub font_family: String,
    pub font_size: usize,
    pub fps_cap: u8,
    pub idle_time_limit: Option<f64>,
    pub last_frame_duration: f64,
    pub line_height: f64,
    pub no_loop: bool,
    pub renderer: Renderer,
    pub rows: Option<usize>,
    pub speed: f64,
    pub theme: Option<Theme>,
    pub show_progress_bar: bool,
}

impl Default for Config {
    fn default() -> Self {
        Self {
            cols: None,
            font_dirs: vec![],
            font_family: String::from(DEFAULT_FONT_FAMILY),
            font_size: DEFAULT_FONT_SIZE,
            fps_cap: DEFAULT_FPS_CAP,
            idle_time_limit: None,
            last_frame_duration: DEFAULT_LAST_FRAME_DURATION,
            line_height: DEFAULT_LINE_HEIGHT,
            no_loop: DEFAULT_NO_LOOP,
            renderer: Default::default(),
            rows: None,
            speed: DEFAULT_SPEED,
            theme: Default::default(),
            show_progress_bar: true,
        }
    }
}

#[derive(Clone, ArgEnum, Default)]
pub enum Renderer {
    #[default]
    Resvg,
    Fontdue,
}

#[derive(Clone, Debug, ArgEnum, Default)]
pub enum Theme {
    Asciinema,
    #[default]
    Dracula,
    GithubDark,
    GithubLight,
    Monokai,
    Nord,
    SolarizedDark,
    SolarizedLight,

    #[clap(skip)]
    Custom(String),
    #[clap(skip)]
    Embedded(theme::Theme),
}

impl TryFrom<Theme> for theme::Theme {
    type Error = anyhow::Error;

    fn try_from(theme: Theme) -> std::result::Result<Self, Self::Error> {
        use Theme::*;

        match theme {
            Asciinema => "121314,cccccc,000000,dd3c69,4ebf22,ddaf3c,26b0d7,b954e1,54e1b9,d9d9d9,4d4d4d,dd3c69,4ebf22,ddaf3c,26b0d7,b954e1,54e1b9,ffffff".parse(),
            Dracula => "282a36,f8f8f2,21222c,ff5555,50fa7b,f1fa8c,bd93f9,ff79c6,8be9fd,f8f8f2,6272a4,ff6e6e,69ff94,ffffa5,d6acff,ff92df,a4ffff,ffffff".parse(),
            GithubDark => "171b21,eceff4,0e1116,f97583,a2fca2,fabb72,7db4f9,c4a0f5,1f6feb,eceff4,6a737d,bf5a64,7abf7a,bf8f57,608bbf,997dbf,195cbf,b9bbbf".parse(),
            GithubLight => "eceff4,171b21,0e1116,f97583,a2fca2,fabb72,7db4f9,c4a0f5,1f6feb,eceff4,6a737d,bf5a64,7abf7a,bf8f57,608bbf,997dbf,195cbf,b9bbbf".parse(),
            Monokai => "272822,f8f8f2,272822,f92672,a6e22e,f4bf75,66d9ef,ae81ff,a1efe4,f8f8f2,75715e,f92672,a6e22e,f4bf75,66d9ef,ae81ff,a1efe4,f9f8f5".parse(),
            Nord => "2e3440,eceff4,3b4252,bf616a,a3be8c,ebcb8b,81a1c1,b48ead,88c0d0,eceff4,3b4252,bf616a,a3be8c,ebcb8b,81a1c1,b48ead,88c0d0,eceff4".parse(),
            SolarizedDark => "002b36,839496,073642,dc322f,859900,b58900,268bd2,d33682,2aa198,eee8d5,002b36,cb4b16,586e75,657b83,839496,6c71c4,93a1a1,fdf6e3".parse(),
            SolarizedLight => "fdf6e3,657b83,073642,dc322f,859900,b58900,268bd2,d33682,2aa198,eee8d5,002b36,cb4b16,586e75,657c83,839496,6c71c4,93a1a1,fdf6e3".parse(),
            Custom(t) => t.parse(),
            Embedded(t) => Ok(t),
        }
    }
}

impl Display for Theme {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        use Theme::*;

        match self {
            Custom(_) => f.write_str("custom"),
            Embedded(_) => f.write_str("embedded"),
            t => write!(f, "{}", format!("{t:?}").to_lowercase()),
        }
    }
}

pub fn run<I: BufRead, O: Write + Send>(input: I, output: O, config: Config) -> Result<()> {
    let (header, events) = asciicast::open(input)?;

    let terminal_size = (
        config.cols.unwrap_or(header.terminal_size.0),
        config.rows.unwrap_or(header.terminal_size.1),
    );

    let itl = config
        .idle_time_limit
        .or(header.idle_time_limit)
        .unwrap_or(DEFAULT_IDLE_TIME_LIMIT);

    let events = asciicast::output(events);
    let events = iter::once((0.0, "".to_owned())).chain(events);
    let events = events::limit_idle_time(events, itl);
    let events = events::accelerate(events, config.speed);
    let events = events::batch(events, config.fps_cap);
    let events = events.collect::<Vec<_>>();
    let count = events.len() as u64;
    let frames = vt::frames(events.into_iter(), terminal_size);

    info!("terminal size: {}x{}", terminal_size.0, terminal_size.1);

    let (font_db, font_families) = fonts::init(&config.font_dirs, &config.font_family)
        .ok_or_else(|| anyhow!("no faces matching font families {}", config.font_family))?;

    info!("selected font families: {:?}", font_families);

    let theme_opt = config
        .theme
        .or_else(|| header.theme.map(Theme::Embedded))
        .unwrap_or(Theme::Dracula);

    info!("selected theme: {}", theme_opt);

    let settings = renderer::Settings {
        terminal_size,
        font_db,
        font_families,
        font_size: config.font_size,
        line_height: config.line_height,
        theme: theme_opt.try_into()?,
    };

    let mut renderer: Box<dyn renderer::Renderer> = match config.renderer {
        Renderer::Fontdue => Box::new(renderer::fontdue(settings)),
        Renderer::Resvg => Box::new(renderer::resvg(settings)),
    };

    let (width, height) = renderer.pixel_size();

    info!("gif dimensions: {}x{}", width, height);

    let repeat = if config.no_loop {
        gifski::Repeat::Finite(0)
    } else {
        gifski::Repeat::Infinite
    };

    let settings = gifski::Settings {
        width: Some(width as u32),
        height: Some(height as u32),
        fast: true,
        repeat,
        ..Default::default()
    };

    let (collector, writer) = gifski::new(settings)?;
    let start_time = Instant::now();

    thread::scope(|s| {
        let writer_handle = s.spawn(move || {
            if config.show_progress_bar {
                let mut pr = gifski::progress::ProgressBar::new(count);
                let result = writer.write(output, &mut pr);
                pr.finish();
                println!();
                result
            } else {
                let mut pr = gifski::progress::NoProgress {};
                writer.write(output, &mut pr)
            }
        });

        for (i, (time, lines, cursor)) in frames.enumerate() {
            let image = renderer.render(lines, cursor);
            let time = if i == 0 { 0.0 } else { time };
            collector.add_frame_rgba(i, image, time + config.last_frame_duration)?;
        }

        drop(collector);
        writer_handle.join().unwrap()?;
        Result::<()>::Ok(())
    })?;

    info!(
        "rendering finished in {}s",
        start_time.elapsed().as_secs_f32()
    );

    Ok(())
}
</file>

<file path="src/main.rs">
use anyhow::{anyhow, Result};
use clap::{ArgAction, ArgEnum, Parser};
use reqwest::header;
use std::io;
use std::{fs::File, io::BufReader, iter};

static USER_AGENT: &str = concat!(env!("CARGO_PKG_NAME"), "/", env!("CARGO_PKG_VERSION"));

#[derive(Clone)]
pub struct Theme(agg::Theme);

#[derive(Clone)]
pub struct ThemeValueParser;

impl clap::builder::TypedValueParser for ThemeValueParser {
    type Value = Theme;

    fn parse_ref(
        &self,
        cmd: &clap::Command,
        arg: Option<&clap::Arg>,
        value: &std::ffi::OsStr,
    ) -> Result<Self::Value, clap::Error> {
        let s = value.to_string_lossy();

        if s.contains(',') {
            Ok(Theme(agg::Theme::Custom(s.to_string())))
        } else {
            clap::value_parser!(agg::Theme)
                .parse_ref(cmd, arg, value)
                .map(Theme)
        }
    }

    fn possible_values(
        &self,
    ) -> Option<Box<dyn Iterator<Item = clap::PossibleValue<'static>> + '_>> {
        Some(Box::new(
            agg::Theme::value_variants()
                .iter()
                .filter_map(|v| v.to_possible_value())
                .chain(iter::once(clap::PossibleValue::new("custom"))),
        ))
    }
}

#[derive(Parser)]
#[clap(author, version, about, long_about = None)]
struct Cli {
    /// asciicast path/filename or URL
    input_filename_or_url: String,

    /// GIF path/filename
    output_filename: String,

    /// Select frame rendering backend
    #[clap(long, arg_enum, default_value_t = agg::Renderer::default())]
    renderer: agg::Renderer,

    /// Specify font family
    #[clap(long, default_value_t = String::from(agg::DEFAULT_FONT_FAMILY))]
    font_family: String,

    /// Specify font size (in pixels)
    #[clap(long, default_value_t = agg::DEFAULT_FONT_SIZE)]
    font_size: usize,

    /// Specify line height
    #[clap(long, default_value_t = agg::DEFAULT_LINE_HEIGHT)]
    line_height: f64,

    /// Select color theme
    #[clap(long, value_parser = ThemeValueParser)]
    theme: Option<Theme>,

    /// Use additional font directory
    #[clap(long)]
    font_dir: Vec<String>,

    /// Adjust playback speed
    #[clap(long, default_value_t = agg::DEFAULT_SPEED)]
    speed: f64,

    /// Disable animation loop
    #[clap(long)]
    no_loop: bool,

    /// Limit idle time to max number of seconds [default: 5]
    #[clap(long)]
    idle_time_limit: Option<f64>,

    /// Set FPS cap
    #[clap(long, default_value_t = agg::DEFAULT_FPS_CAP)]
    fps_cap: u8,

    /// Set last frame duration
    #[clap(long, default_value_t = agg::DEFAULT_LAST_FRAME_DURATION)]
    last_frame_duration: f64,

    /// Override terminal width (number of columns)
    #[clap(long)]
    cols: Option<usize>,

    /// Override terminal height (number of rows)
    #[clap(long)]
    rows: Option<usize>,

    /// Enable verbose logging
    #[clap(short, long, action = ArgAction::Count)]
    verbose: u8,
}

fn download(url: &str) -> Result<impl io::Read> {
    let client = reqwest::blocking::Client::builder()
        .user_agent(USER_AGENT)
        .gzip(true)
        .build()?;

    let request = client
        .get(url)
        .header(
            header::ACCEPT,
            header::HeaderValue::from_static("application/x-asciicast,application/json"),
        )
        .build()?;

    let response = client.execute(request)?.error_for_status()?;

    let ct = response
        .headers()
        .get(header::CONTENT_TYPE)
        .and_then(|hv| hv.to_str().ok())
        .ok_or_else(|| anyhow!("unknown content type".to_owned()))?;

    if ct != "application/x-asciicast" && ct != "application/json" {
        return Err(anyhow!(format!("{ct} is not supported")));
    }

    Ok(Box::new(response))
}

fn reader(path: &str) -> Result<Box<dyn io::Read>> {
    if path == "-" {
        Ok(Box::new(io::stdin()))
    } else if path.starts_with("http://") || path.starts_with("https://") {
        Ok(Box::new(download(path)?))
    } else {
        Ok(Box::new(File::open(path)?))
    }
}

fn main() -> Result<()> {
    let cli = Cli::parse();

    let log_level = match cli.verbose {
        0 => "error",
        1 => "info",
        _ => "debug",
    };

    let env = env_logger::Env::default().default_filter_or(log_level);
    env_logger::Builder::from_env(env)
        .format_timestamp(None)
        .init();

    let config = agg::Config {
        cols: cli.cols,
        font_dirs: cli.font_dir,
        font_family: cli.font_family,
        font_size: cli.font_size,
        fps_cap: cli.fps_cap,
        idle_time_limit: cli.idle_time_limit,
        last_frame_duration: cli.last_frame_duration,
        line_height: cli.line_height,
        no_loop: cli.no_loop,
        renderer: cli.renderer,
        rows: cli.rows,
        speed: cli.speed,
        theme: cli.theme.map(|theme| theme.0),
        show_progress_bar: true,
    };

    let input = BufReader::new(reader(&cli.input_filename_or_url)?);
    let mut output = File::create(&cli.output_filename)?;
    agg::run(input, &mut output, config)
}
</file>

<file path="src/renderer.rs">
mod fontdue;
mod resvg;

use imgref::ImgVec;
use rgb::{RGB8, RGBA8};

use crate::theme::Theme;

pub trait Renderer {
    fn render(&mut self, lines: Vec<avt::Line>, cursor: Option<(usize, usize)>) -> ImgVec<RGBA8>;
    fn pixel_size(&self) -> (usize, usize);
}

pub struct Settings {
    pub terminal_size: (usize, usize),
    pub font_db: fontdb::Database,
    pub font_families: Vec<String>,
    pub font_size: usize,
    pub line_height: f64,
    pub theme: Theme,
}

pub fn resvg<'a>(settings: Settings) -> resvg::ResvgRenderer<'a> {
    resvg::ResvgRenderer::new(settings)
}

pub fn fontdue(settings: Settings) -> fontdue::FontdueRenderer {
    fontdue::FontdueRenderer::new(settings)
}

struct TextAttrs {
    foreground: Option<avt::Color>,
    background: Option<avt::Color>,
    bold: bool,
    faint: bool,
    italic: bool,
    underline: bool,
}

fn text_attrs(
    pen: &avt::Pen,
    cursor: &Option<(usize, usize)>,
    col: usize,
    row: usize,
    theme: &Theme,
) -> TextAttrs {
    let mut foreground = pen.foreground();
    let mut background = pen.background();
    let inverse = cursor.map_or(false, |cursor| cursor.0 == col && cursor.1 == row);

    if pen.is_bold() {
        if let Some(avt::Color::Indexed(n)) = foreground {
            if n < 8 {
                foreground = Some(avt::Color::Indexed(n + 8));
            }
        }
    }

    if pen.is_blink() {
        if let Some(avt::Color::Indexed(n)) = background {
            if n < 8 {
                background = Some(avt::Color::Indexed(n + 8));
            }
        }
    }

    if pen.is_inverse() ^ inverse {
        let fg = background.unwrap_or(avt::Color::RGB(theme.background));
        let bg = foreground.unwrap_or(avt::Color::RGB(theme.foreground));
        foreground = Some(fg);
        background = Some(bg);
    }

    TextAttrs {
        foreground,
        background,
        bold: pen.is_bold(),
        faint: pen.is_faint(),
        italic: pen.is_italic(),
        underline: pen.is_underline(),
    }
}

fn color_to_rgb(c: &avt::Color, theme: &Theme) -> RGB8 {
    match c {
        avt::Color::RGB(c) => *c,
        avt::Color::Indexed(c) => theme.color(*c),
    }
}
</file>

<file path="src/theme.rs">
use std::str::FromStr;

use anyhow::bail;
use rgb::RGB8;

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct Theme {
    pub background: RGB8,
    pub foreground: RGB8,
    palette: [RGB8; 16],
}

fn parse_hex_triplet(triplet: &str) -> anyhow::Result<RGB8> {
    if triplet.len() < 6 || triplet.len() > 6 {
        bail!("{} is not a hex triplet", triplet);
    }

    let r = u8::from_str_radix(&triplet[0..2], 16)?;
    let g = u8::from_str_radix(&triplet[2..4], 16)?;
    let b = u8::from_str_radix(&triplet[4..6], 16)?;

    Ok(RGB8::new(r, g, b))
}

impl FromStr for Theme {
    type Err = anyhow::Error;

    fn from_str(s: &str) -> Result<Self, Self::Err> {
        let mut palette = [RGB8::default(); 16];

        let colors = s
            .split(',')
            .filter(|s| !s.is_empty())
            .map(parse_hex_triplet)
            .collect::<anyhow::Result<Vec<RGB8>>>()?;

        if colors.len() != 10 && colors.len() != 18 {
            bail!("expected 10 or 18 hex triplets, got {}", colors.len());
        }

        let background = colors[0];
        let foreground = colors[1];

        for (i, color) in colors.into_iter().skip(2).cycle().take(16).enumerate() {
            palette[i] = color;
        }

        Ok(Self {
            background,
            foreground,
            palette,
        })
    }
}

impl Theme {
    pub fn color(&self, color: u8) -> RGB8 {
        match color {
            0..=15 => self.palette[color as usize],

            16..=231 => {
                let n = color - 16;
                let mut r = ((n / 36) % 6) * 40;
                let mut g = ((n / 6) % 6) * 40;
                let mut b = (n % 6) * 40;

                if r > 0 {
                    r += 55;
                }

                if g > 0 {
                    g += 55;
                }

                if b > 0 {
                    b += 55;
                }

                RGB8::new(r, g, b)
            }

            232.. => {
                let v = 8 + 10 * (color - 232);

                RGB8::new(v, v, v)
            }
        }
    }
}

#[cfg(test)]
mod tests {
    use super::Theme;
    use rgb::RGB8;

    #[test]
    fn parse_invalid() {
        assert!("".parse::<Theme>().is_err());

        assert!("foo".parse::<Theme>().is_err());

        assert!("000000,111111,222222,333333,444444"
            .parse::<Theme>()
            .is_err());

        assert!(
            "xxxxxx,111111,222222,333333,444444,555555,666666,777777,888888,999999"
                .parse::<Theme>()
                .is_err()
        );
    }

    #[test]
    fn parse_8_color_palette() {
        let result = "bbbbbb,ffffff,000000,111111,222222,333333,444444,555555,666666,777777"
            .parse::<Theme>();

        assert!(result.is_ok());

        let theme = result.unwrap();

        assert_eq!(
            theme.background,
            RGB8 {
                r: 0xbb,
                g: 0xbb,
                b: 0xbb
            }
        );

        assert_eq!(
            theme.foreground,
            RGB8 {
                r: 0xff,
                g: 0xff,
                b: 0xff
            }
        );

        assert_eq!(
            theme.palette,
            [
                RGB8 {
                    r: 0x00,
                    g: 0x00,
                    b: 0x00
                },
                RGB8 {
                    r: 0x11,
                    g: 0x11,
                    b: 0x11
                },
                RGB8 {
                    r: 0x22,
                    g: 0x22,
                    b: 0x22
                },
                RGB8 {
                    r: 0x33,
                    g: 0x33,
                    b: 0x33
                },
                RGB8 {
                    r: 0x44,
                    g: 0x44,
                    b: 0x44
                },
                RGB8 {
                    r: 0x55,
                    g: 0x55,
                    b: 0x55
                },
                RGB8 {
                    r: 0x66,
                    g: 0x66,
                    b: 0x66
                },
                RGB8 {
                    r: 0x77,
                    g: 0x77,
                    b: 0x77
                },
                RGB8 {
                    r: 0x00,
                    g: 0x00,
                    b: 0x00
                },
                RGB8 {
                    r: 0x11,
                    g: 0x11,
                    b: 0x11
                },
                RGB8 {
                    r: 0x22,
                    g: 0x22,
                    b: 0x22
                },
                RGB8 {
                    r: 0x33,
                    g: 0x33,
                    b: 0x33
                },
                RGB8 {
                    r: 0x44,
                    g: 0x44,
                    b: 0x44
                },
                RGB8 {
                    r: 0x55,
                    g: 0x55,
                    b: 0x55
                },
                RGB8 {
                    r: 0x66,
                    g: 0x66,
                    b: 0x66
                },
                RGB8 {
                    r: 0x77,
                    g: 0x77,
                    b: 0x77
                },
            ]
        );
    }

    #[test]
    fn parse_16_color_palette() {
        let result = "bbbbbb,ffffff,000000,111111,222222,333333,444444,555555,666666,777777,888888,999999,aaaaaa,bbbbbb,cccccc,dddddd,eeeeee,ffffff".parse::<Theme>();

        assert!(result.is_ok());

        let theme = result.unwrap();

        assert_eq!(
            theme.background,
            RGB8 {
                r: 0xbb,
                g: 0xbb,
                b: 0xbb
            }
        );

        assert_eq!(
            theme.foreground,
            RGB8 {
                r: 0xff,
                g: 0xff,
                b: 0xff
            }
        );

        assert_eq!(
            theme.palette,
            [
                RGB8 {
                    r: 0x00,
                    g: 0x00,
                    b: 0x00
                },
                RGB8 {
                    r: 0x11,
                    g: 0x11,
                    b: 0x11
                },
                RGB8 {
                    r: 0x22,
                    g: 0x22,
                    b: 0x22
                },
                RGB8 {
                    r: 0x33,
                    g: 0x33,
                    b: 0x33
                },
                RGB8 {
                    r: 0x44,
                    g: 0x44,
                    b: 0x44
                },
                RGB8 {
                    r: 0x55,
                    g: 0x55,
                    b: 0x55
                },
                RGB8 {
                    r: 0x66,
                    g: 0x66,
                    b: 0x66
                },
                RGB8 {
                    r: 0x77,
                    g: 0x77,
                    b: 0x77
                },
                RGB8 {
                    r: 0x88,
                    g: 0x88,
                    b: 0x88
                },
                RGB8 {
                    r: 0x99,
                    g: 0x99,
                    b: 0x99
                },
                RGB8 {
                    r: 0xaa,
                    g: 0xaa,
                    b: 0xaa
                },
                RGB8 {
                    r: 0xbb,
                    g: 0xbb,
                    b: 0xbb
                },
                RGB8 {
                    r: 0xcc,
                    g: 0xcc,
                    b: 0xcc
                },
                RGB8 {
                    r: 0xdd,
                    g: 0xdd,
                    b: 0xdd
                },
                RGB8 {
                    r: 0xee,
                    g: 0xee,
                    b: 0xee
                },
                RGB8 {
                    r: 0xff,
                    g: 0xff,
                    b: 0xff
                },
            ]
        );
    }
}
</file>

<file path="src/vt.rs">
use log::debug;

pub fn frames(
    stdout: impl Iterator<Item = (f64, String)>,
    terminal_size: (usize, usize),
) -> impl Iterator<Item = (f64, Vec<avt::Line>, Option<(usize, usize)>)> {
    let mut vt = avt::Vt::builder()
        .size(terminal_size.0, terminal_size.1)
        .scrollback_limit(0)
        .build();

    let mut prev_cursor = None;

    stdout.filter_map(move |(time, data)| {
        let changed_lines = vt.feed_str(&data).lines;
        let cursor: Option<(usize, usize)> = vt.cursor().into();

        if !changed_lines.is_empty() || cursor != prev_cursor {
            prev_cursor = cursor;
            let lines = vt.view().to_vec();

            Some((time, lines, cursor))
        } else {
            prev_cursor = cursor;
            debug!("skipping frame with no visual changes: {:?}", data);

            None
        }
    })
}

#[cfg(test)]
mod tests {
    #[test]
    fn frames() {
        let stdout = [
            (0.0, "foo".to_owned()),
            (1.0, "\x1b[0m".to_owned()),
            (2.0, "bar".to_owned()),
            (3.0, "!".to_owned()),
        ];

        let fs = super::frames(stdout.into_iter(), (4, 2)).collect::<Vec<_>>();

        assert_eq!(fs.len(), 3);

        let (time, lines, cursor) = &fs[0];
        let lines: Vec<String> = lines.iter().map(|l| l.text()).collect();

        assert_eq!(*time, 0.0);
        assert_eq!(*cursor, Some((3, 0)));
        assert_eq!(lines[0], "foo ");
        assert_eq!(lines[1], "    ");

        let (time, lines, cursor) = &fs[1];
        let lines: Vec<String> = lines.iter().map(|l| l.text()).collect();

        assert_eq!(*time, 2.0);
        assert_eq!(*cursor, Some((2, 1)));
        assert_eq!(lines[0], "foob");
        assert_eq!(lines[1], "ar  ");

        let (time, lines, cursor) = &fs[2];
        let lines: Vec<String> = lines.iter().map(|l| l.text()).collect();

        assert_eq!(*time, 3.0);
        assert_eq!(*cursor, Some((3, 1)));
        assert_eq!(lines[0], "foob");
        assert_eq!(lines[1], "ar! ");
    }
}
</file>

<file path=".dockerignore">
target/
.git*
Dockerfile
</file>

<file path=".gitignore">
.envrc
.direnv
/target
result
</file>

<file path="Cargo.toml">
[package]
name = "agg"
version = "1.5.0"
edition = "2021"

# See more keys and their definitions at https://doc.rust-lang.org/cargo/reference/manifest.html

[dependencies]
anyhow = "1"
avt = "0.14.0"
clap = { version = "3.2.15", features = ["derive"] }
env_logger = "0.10"
fontdb = "0.22.0"
fontdue = "0.7"
gifski = "1"
imgref = "1"
log = "0.4"
reqwest = { version = "0.12.8", default-features = false, features = ["blocking", "rustls-tls-native-roots", "gzip"] }
resvg = { version = "0.44.0", features = ["text"] } # TODO remove default features
rgb = "0.8"
serde = { version = "1.0.137", features = ["derive"] }
serde_json = "1.0.81"
shellexpand = "3.1.0"
tiny-skia = "0.11.4"
usvg = "0.44.0"
</file>

<file path="default.nix">
(import (fetchTarball {
  url = "https://github.com/edolstra/flake-compat/archive/b4a34015c698c7793d592d66adbab377907a2be8.tar.gz";
  sha256 = "1qc703yg0babixi6wshn5wm2kgl5y1drcswgszh4xxzbrwkk9sv7";
}) { src = ./.; }).defaultNix
</file>

<file path="Dockerfile">
FROM rust:buster AS builder

COPY . /usr/src/

WORKDIR /usr/src

RUN ["cargo", "build", "-r"]

FROM rust:buster

LABEL org.opencontainers.image.authors="kayvan.sylvan@gmail.com"

COPY --from=builder /usr/src/target/release/agg /usr/local/bin/

WORKDIR /data

ENTRYPOINT [ "/usr/local/bin/agg" ]
</file>

<file path="flake.lock">
{
  "nodes": {
    "naersk": {
      "inputs": {
        "nixpkgs": "nixpkgs"
      },
      "locked": {
        "lastModified": 1721727458,
        "narHash": "sha256-r/xppY958gmZ4oTfLiHN0ZGuQ+RSTijDblVgVLFi1mw=",
        "owner": "nix-community",
        "repo": "naersk",
        "rev": "3fb418eaf352498f6b6c30592e3beb63df42ef11",
        "type": "github"
      },
      "original": {
        "owner": "nix-community",
        "ref": "master",
        "repo": "naersk",
        "type": "github"
      }
    },
    "nixpkgs": {
      "locked": {
        "lastModified": 0,
        "narHash": "sha256-9/79hjQc9+xyH+QxeMcRsA6hDyw6Z9Eo1/oxjvwirLk=",
        "path": "/nix/store/s9hbmmf7hgg7imnm5q6ny7gznbh0amfy-source",
        "type": "path"
      },
      "original": {
        "id": "nixpkgs",
        "type": "indirect"
      }
    },
    "nixpkgs_2": {
      "locked": {
        "lastModified": 1728031656,
        "narHash": "sha256-JXumn7X+suKEcehp4rchSvBzIboqyybQ5bLK4wk7gQU=",
        "owner": "NixOS",
        "repo": "nixpkgs",
        "rev": "eeeb90a1dd3c9bea3afdbc76fd34d0fb2a727c7a",
        "type": "github"
      },
      "original": {
        "owner": "NixOS",
        "ref": "nixpkgs-unstable",
        "repo": "nixpkgs",
        "type": "github"
      }
    },
    "root": {
      "inputs": {
        "naersk": "naersk",
        "nixpkgs": "nixpkgs_2",
        "utils": "utils"
      }
    },
    "systems": {
      "locked": {
        "lastModified": 1681028828,
        "narHash": "sha256-Vy1rq5AaRuLzOxct8nz4T6wlgyUR7zLU309k9mBC768=",
        "owner": "nix-systems",
        "repo": "default",
        "rev": "da67096a3b9bf56a91d16901293e51ba5b49a27e",
        "type": "github"
      },
      "original": {
        "owner": "nix-systems",
        "repo": "default",
        "type": "github"
      }
    },
    "utils": {
      "inputs": {
        "systems": "systems"
      },
      "locked": {
        "lastModified": 1726560853,
        "narHash": "sha256-X6rJYSESBVr3hBoH0WbKE5KvhPU5bloyZ2L4K60/fPQ=",
        "owner": "numtide",
        "repo": "flake-utils",
        "rev": "c1dfcf08411b08f6b8615f7d8971a2bfa81d5e8a",
        "type": "github"
      },
      "original": {
        "owner": "numtide",
        "repo": "flake-utils",
        "type": "github"
      }
    }
  },
  "root": "root",
  "version": 7
}
</file>

<file path="flake.nix">
{
  inputs = {
    naersk.url = "github:nix-community/naersk/master";
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
    utils.url = "github:numtide/flake-utils";
  };
  outputs = { self, nixpkgs, utils, naersk }:
    utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs { inherit system; };
        naersk-lib = pkgs.callPackage naersk { };
      in {
        defaultPackage = naersk-lib.buildPackage {
          pname = "agg";
          src = ./.;
        };
        defaultApp = utils.lib.mkApp { drv = self.defaultPackage."${system}"; };
        devShell = with pkgs;
          mkShell {
            buildInputs =
              [ cargo rustc rustfmt pre-commit rustPackages.clippy ];
            RUST_SRC_PATH = rustPlatform.rustLibSrc;
          };
      });
}
</file>

<file path="README.md">
# agg - asciinema gif generator

__agg__ is a command-line tool for generating animated GIF files from terminal
session recordings.

It supports conversion from [asciicast
v2](https://github.com/asciinema/asciinema/blob/master/doc/asciicast-v2.md)
files produced by [asciinema recorder](https://github.com/asciinema/asciinema).
It uses Kornel Lesiński's excellent
[gifski](https://github.com/ImageOptim/gifski) library to produce optimized,
high quality GIF output with accurate frame timing.

Example GIF file generated with agg:

![Example GIF file generated with agg](demo.gif)

Check out the [agg docs](https://docs.asciinema.org/manual/agg/) for
installation and usage overview.

agg is a successor to
[asciicast2gif](https://github.com/asciinema/asciicast2gif).

## Building

Building from source requires [Rust](https://www.rust-lang.org/) compiler
(1.56.0 or later) and [Cargo package manager](https://doc.rust-lang.org/cargo/).
You can install both with [rustup](https://rustup.rs/).

To download source code, build agg binary and install it in `$HOME/.cargo/bin`
run:

```bash
cargo install --git https://github.com/asciinema/agg
```

You need to ensure `$HOME/.cargo/bin` is in your shell's `$PATH`.

Alternatively, you can manually download source code and build agg binary with:

```bash
git clone https://github.com/asciinema/agg
cd agg
cargo build --release
```

This produces an executable file in _release mode_ (`--release`) at
`target/release/agg`. There are no other build artifacts so you can copy the
binary to a directory in your `$PATH`.

### Building with Docker

Alternatively, if you have Docker, Podman or another Docker-compatible tool
installed you can use it to build agg container image. This doesn't require Rust
toolchain installed on your machine.

Build the image with the following command:

```sh
docker build -t agg .
```

Then run agg like this:

```sh
docker run --rm -it -u $(id -u):$(id -g) -v $PWD:/data agg demo.cast demo.gif
```

If you use Podman in root-less mode:

```sh
podman run --rm -it -v $PWD:/data agg demo.cast demo.gif
```

## Consulting

If you're interested in customization of agg or any other asciinema component to
for your corporate needs, check [asciinema consulting
services](https://docs.asciinema.org/consulting/).

## License

© 2022 Marcin Kulik.

All code is licensed under the Apache License, Version 2.0. See LICENSE file for details.
</file>

<file path="shell.nix">
(import (fetchTarball {
  url = "https://github.com/edolstra/flake-compat/archive/b4a34015c698c7793d592d66adbab377907a2be8.tar.gz";
  sha256 = "1qc703yg0babixi6wshn5wm2kgl5y1drcswgszh4xxzbrwkk9sv7";
}) { src = ./.; }).shellNix
</file>

</files>
"""

TestAggToText = (
    StringNode(question + cargo + context) >>
    MultiShotLLMRun(
        ExtractCode(keep_main=True) >> CargoRun(cargo, input="woof".encode()),
    ) >>
    EqualEvaluator("woof")
)

if __name__ == "__main__":
    print(run_test(TestAggToText))
