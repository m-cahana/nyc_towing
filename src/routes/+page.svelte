<script>
    import Footer from "$lib/components/footer.svelte";
    import Barplot from "$lib/components/barplot.svelte";
    import TowPlates from "$lib/components/tow_plates.svelte";

    import { onMount } from 'svelte';

    onMount(() => {
        window.scrollTo(0, 0);
    });
</script>

<main>
	<h1>Tens of Thousands of Recidivist Speeders Evaded The Law Last Year</h1>
    <div class="subtitle">June 2025</div>

    <p>
        As <a href="https://streetsblog.org/2025/04/10/thousands-of-cars-speed-rampantly-through-new-york-citys-school-zones-without-facing-consequences/" target="_blank">Streetsblog reported in April</a>, thousands of cars speed rampantly through New York City's school zones without facing consequences. This occurs, in part, because the city doesn't cap the number of speeding fines a driver can rack up; as long as a driver pays their fines, they can continue speedingly endlessly.
    </p>

    <p>
        But this investigation identifies another factor behind the city's unsafe streets: the laws currently on the books to deter speeding often go unenforced. Even if drivers don't pay their fines, they can get away with repeated speeding. Consider the chart below: 
    </p>

    <Barplot />

    <p>
        This chart shows that as drivers commit more speeding violations, they pay a smaller share of their fines. Drivers with 1-5 violations pay almost all of their fines, but drivers who commit 100+ violations only pay a quarter of their fines. Why is that?
    </p>

    <p>
        It could be because recidivist speeders face very high fine totals, and find them difficult to pay off. But it's also possible that these recidivist speeders have learned to game the city's fine system. Through repeated violations, they might have uncovered a useful loophole: the city doesn't actually force all drivers to pay their fines. 
    </p>

    <p>
        The city's laws currently dictate that any driver who accrues over $350 in fines (which translates to 5 unpaid school zone tickets when you factor in late fees), and doesn't pay them within 75 days, will be deemed "in judgement". In theory, vehicles in judgement should be booted, and then towed if a driver doesn't pay up their judgement debt <a href="https://www.nyc.gov/site/finance/vehicles/services-booting.page" target="_blank">within 48 hours of the boot</a>. This law is meant to ensure drivers actually pay their fines, and face real inconvenience when ignoring them.
    </p>

    <p>
        But our investigation shows something else happening. Every month, thousands of recidivist speeders enter judgement, never pay off their fine debt, and never get booted or towed either. 
    </p>

    <TowPlates />

    <p>
        These scofflaws represent over $24 million in lost revenue for the city, in the form of uncollected fines. 
        More importantly, they represent a continued risk to public safety, racking up over 80,000 school zone violations that would have never occurred if the city's laws were properly enforced. 
    </p>

    <p>
        But since enforcement isn't comprehensive, tens of thousands of drivers continue to speed long after they should have been stopped. Some of them must have figured out that they can just get away with it. And why not? There's ample precedent for drivers speeding, ignoring fines, and never paying up. 
    </p>
    
</main>

<Footer />


<style>
	main {
		margin: 0 auto;
		max-width: 800px;
		padding: 1rem;
        font-family: "Helvetica";
		text-align: center;
	}


	h1 {
		font-size: 36px;
        font-style: italic;
        font-weight: 300;
        margin-bottom: 0.2rem;
	}

    p {
        font-size: 16px;
        text-align: left;
        font-weight: 300;
    }

    .subtitle {
        font-size: 20px;
        font-style: italic;
        font-weight: 300;
        margin-top: 0;
    }
</style>