# __Call Analyzer App Architecture__

__App Overview__

``` mermaid
  graph LR;
    A[User] -->|Interacts with| B[Frontend];
    B --> C[Backend];
    C --> B
    C --> D[AI Model]
    D --> C
```

__Frontend-Backend interaction__
``` mermaid
  graph LR;
    A[Frontend] -->|async POST: audio file| B[Backend];
    B -->|async GET: Fetch transcript| A;
```

__Backend-AI Model interaction__
``` mermaid
  graph LR;
    A[Backend] -->|send audio file| B[Whisper API];
    B -->|Return transcript| A;
```

<div class="grid cards" markdown>
  - [__<- Table of Content__](index.md)
  - [__App Functionality ->__](functionality.md)
</div>