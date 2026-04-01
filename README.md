# LinkedIn Post Generation Workflow

Generate high-signal LinkedIn content backed by the latest trends in the industry from Reddit & Hacker News.

## Summary

- Dynamic Trend Ingestion: Integrated Algolia HN Search and Reddit RSS to ensure content is grounded in the latest shifts in the industry
- Multi-Model Support: Built a modular router supporting Aliyun Qwen (DashScope), OpenAI, Gemini, and Grok.
- Prompt Engineering: Developed a specialized synthesis prompt that enforces "Broken Rhythm" and "Pattern Interrupts" to compete for the top 1% of LinkedIn distribution.

## Workflow Design

- Data is ingested from Reddit (RSS) and Hacker News (Algolia) **on-demand** since 

- Prompts use an adversarial loop to criticize and revise the post, ensuring higher quality and reducing AI slop

## Tradeoffs

- Posts are ingested on-demand instead of regularly in the background. This has its pros and cons: 
    - Pros: content is guaranteed to be the newest content; simpler design
    - Cons: we don't maintain a larger pool of content; have to search from scratch every time
    - Alternative design: maintain a persistent database of posts ordered by timestamp, regularly add new posts & delete old posts
- In terms of code design, everything is in one file and there is minimal abstraction (helper functions)
    - Pros: simple design
    - Cons: harder to maintain or write unit tests, or run as API/backend later
- Each post requires 3 LLM calls (and searching also requires LLM calls)
    - Tradeoff: Quality over cost and speed
- No persistence across sections (this is an MVP/demo after all)
    - Tradeoff: convenience over scalability. *Sometimes we want to build a working demo fast*.

## Future Improvements

- Sift through posts to find the highest-signal content on Reddit & HN, avoiding low quality posts
    - Filter posts by upvotes/comments/recency

- Customize prompts for different industries of the user's choosing

- For a better effect, we would want to finetune an LLM on lots and lots of high quality LinkedIn posts. But this time I had to make use of limited resources & time.