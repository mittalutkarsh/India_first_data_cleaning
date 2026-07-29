# The most important decision when you train an LLM (and it's not the architecture)

Everyone wants to talk about the architecture.

How many layers, which attention variant, the newest optimizer, the clever positional encoding. And I get it, that stuff is fun. But here is the uncomfortable truth: the architecture is mostly solved. If you and I sat down and designed the most beautiful transformer ever, wired up flash attention and a perfect tokenizer, and then pointed it at a random folder of data and hit "train," we would get garbage.

The thing that actually decides whether your model is brilliant or useless is much less glamorous. It's the data. Specifically, it's *what* data, in *what* proportions, in *what* order.

That's the data mixture and the curriculum. Let's talk about it, because once you understand this, everything else gets easier.

## A model becomes what it eats

Think of the mixture as a diet.

You have a fixed budget of tokens to train on, say a few trillion. That budget is your total calories for the season. Now you have to decide how to spend it. How much English? How much code? How much math? How much of the Indian languages you actually care about? Every slice you hand to one skill is a slice you take away from another, because the budget doesn't grow.

And here is the part people underestimate: this single set of proportions *is* the personality of the model.

Pour most of your budget into code and starve the general web, and you get a model that writes flawless programs and has no common sense. Ask it to count the index fingers in a room and it will cheerfully write a function that asks you how many index fingers each person has. The code runs. It just doesn't understand the world. Common sense lives on the messy general web, and if you don't feed it, it simply won't be there.

So the mixture isn't a config file. It's a design decision about who the model is going to be.

## The trap: wanting a number you can't actually cook

Here's the mistake almost everyone makes on their first plan, and I made it too.

You decide your model should be great at agentic work, tool calling, multi-step tasks. So you write down "16% agentic" and feel good about it. Sixteen percent of a few trillion tokens is a lot of agentic data.

Then you go to the pantry.

And you discover you have almost none. The good, cleaned, actually-trainable agentic traces you own amount to a rounding error. To fill 16% you would have to repeat what little you have thousands of times, which doesn't teach the model to be a good agent. It teaches it to memorize a handful of examples.

This is the single most useful exercise in the whole plan: put "what I want" next to "what I actually have," in tokens, side by side. The lanes where you want far more than you own are *starved*. And that gap is not a failure of the plan. It's the most important output of the plan, because it tells you exactly where to point your data collection next.

A desired number and an executable number are two different things. A good plan says both, out loud.

## Order matters as much as amount

Now for the part people forget entirely: *when* the model sees the data.

You don't teach a child quantum mechanics in nursery. You start broad and simple, let them learn to read and pick up basic common sense, and only then do you introduce harder and narrower material. Training is the same. Start with broad web text so the model learns language and how the world works. Then gradually shift toward code, science, reasoning, and the really long, hard problems.

And you save your very best material for the end.

Right before the finish, there's a short cooldown phase where the learning rate winds down to almost nothing. Whatever the model sees in that window lands with unusual force. It's the young Einstein, finally ready, sitting down to write the good paper. So you hold back your cleanest, highest-quality data, the PhD-level stuff, and you spend it precisely then. Feed that data too early and the model just isn't ready to absorb it; it washes over an infant.

One warning from painful experience: don't switch the diet abruptly. If you jump straight from easy web text to hard reasoning problems, the training destabilizes, the gradients spike, and you spend days fighting it. You have to blend the phases into each other, the way a good curriculum eases you from one grade into the next rather than dropping you into a PhD seminar the day after high school.

## Your own data selector will quietly betray you

This one is subtle, and it's my favorite.

During training you often run an automatic selector that watches the model and keeps the data that seems to help it most. Sounds great. But a common trick is that the selector only glances at the first few hundred tokens of each example, and it judges "helpful" against a set of mostly English, mostly coding benchmarks.

So what does it do with your precious Indian-language data? It sees a few hundred tokens that don't move its English-coding scores and it throws them away. What does it do with a long agentic trace? The first few hundred tokens look like a boring log, so it tosses that too.

Your selector, left alone, will quietly starve the exact capabilities you're trying to build.

The blunt fix is a floor: a hard rule that says these lanes never drop below some minimum, no matter what the selector prefers, and it's enforced constantly, not just averaged over the whole run. The better fix is to teach the selector to care about the right things in the first place, by scoring it against benchmarks that actually include your target languages and your agentic tasks. Either way, the lesson is the same: don't let a myopic optimizer decide what your model is allowed to become.

## Every number here is a guess until a cheap experiment proves it

I want to leave you with the one principle that runs through all of this.

Every proportion, every ordering, every floor I just described is a hypothesis. It feels like a decision, it's written down like a decision, but until you've tested it, it's a guess wearing a suit.

And you don't test guesses on the giant, expensive run. You test them small. You train a one-billion and a three-billion parameter model, cheap and fast, on competing recipes, and you see which one actually wins on the evaluations you care about. Only the recipes that survive that get promoted to the full-scale run.

One catch worth knowing: at one billion parameters, the hardest benchmarks read zero for everyone, so they tell you nothing. Test on the evals that actually have signal at that size, and look at whether one recipe *ranks* above another, not the exact number, because the exact numbers move as the model grows.

## The bottom line

The architecture gets the headlines, but the data mixture and curriculum are what actually make or break the model.

Decide what capabilities you want. Then be honest about what you can actually feed, and treat the gaps as your shopping list. Teach the model in an order that goes from broad to deep, and save your best data for last. Protect the fragile, valuable lanes from your own selector. And remember, always, that none of your numbers are true until a small, cheap experiment says they are.

Get this right, and the rest of training is the easy part.
