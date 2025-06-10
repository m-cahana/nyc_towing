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
        As <a href="https://streetsblog.org/2025/04/10/thousands-of-cars-speed-rampantly-through-new-york-citys-school-zones-without-facing-consequences/" target="_blank">Streetsblog reported in April</a>, thousands of cars speed rampantly through New York City's school zones without facing consequences. This occurs, in part, because the city doesn't cap the number of speeding tickets a driver can rack up; as long as a driver pays their tickets, they can continue speedingly endlessly.
    </p>

    <p>
        But this investigation identifies another factor behind the city's unsafe streets: the laws currently on the books to deter speeding often go unenforced. Even if drivers don't pay their fines, they can get away with repeatedly speeding. Consider the chart below: 
    </p>

    <Barplot />

    <p>
        This chart shows that as drivers commit more speeding violations, they pay a smaller share of their fines. Drivers with 1-5 violations pay almost all of their fines, but drivers who commit 100+ violations only pay a quarter of their fines. Why is that?
    </p>

    <p>
        It could be because recidivist speeders face very high fine totals, and find them difficult to pay off. But it's also possible that these recidivist speeders have learned to game the city's ticketing system. Through repeated violations, they might have uncovered a useful loophole: the city doesn't actually force all drivers to pay their fines. 
    </p>

    <p>
        The city's laws currently say that any driver who accrues over $350 in fines (which translates to 5 unpaid school zone tickets when you factor in late fees) and doesn't pay them within 75 days will be deemed "in judgement". In theory, vehicles in judgement should be booted, and subsequently towed if a driver doesn't pay up their judgement debt <a href="https://www.nyc.gov/site/finance/vehicles/services-booting.page" target="_blank">within 48 hours of the boot</a>. This law is meant to ensure that a driver faces real consequences for ignoring unpaid fines.
    </p>

    <p>
        But our investigation shows that every month, thousands of recidivist speeders enter judgement, never pay off their fine debt, and never get booted or towed. 
    </p>

    <TowPlates />

    <p>
        These scofflaw drivers represent over $24 million in lost revenue for the city in the form of uncollected fines. Over $5.7 million of these fines were accrued after these vehicles entered judgement, the result of over 80,000 school zone violations that should have never occurred. 
    </p>

    <p>
        Most importantly, these drivers represent a continued risk to the public. A risk that the city, according to its own laws, should prevent. But whether through negligence or lack of resources, it's been unable to do so. Tens of thousands of them continue to speed through school zones when they should be booted. At least some must have figured out that they can get away with it. 
    </p>

    <Footer />
</main>


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