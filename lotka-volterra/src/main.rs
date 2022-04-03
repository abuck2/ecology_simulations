fn run_simulation(initial:Vec<u32>, n_iter:u32, r:Vec<f32>, k:Vec<u32>, competition:Vec<f32>) -> (Vec<u32>,Vec<u32> ) {
    
    let mut population_1 = Vec::<u32>::new();
    let mut population_2 = Vec::<u32>::new();
    for n in 1..n_iter {
        let last_pop = last_population(n, initial.clone(), population_1.clone(), population_2.clone());
        let pop1:u32 = last_pop.0;//superfluous
        let pop2:u32 = last_pop.1;//that as well
        

        let newpop_1:i32 = update_simulation(pop1, pop2, r[0], k[0], competition[1]).round() as i32;
        let newpop_2:i32 = update_simulation(pop2, pop1, r[1], k[1], competition[0]).round() as i32;
        
        let pos_pop_1:u32 = check_extinction(newpop_1);
        let pos_pop_2:u32 = check_extinction(newpop_2);
        println!("Population for species 1 at turn {} is {}", n, pos_pop_1);
        println!("Population for species 2 at turn {} is {}", n, pos_pop_2);

        population_1.push(pos_pop_1);
        population_2.push(pos_pop_2);
    }
    (population_1, population_2)
}

fn last_population(n:u32, initial:Vec<u32>, population_1:Vec<u32>, population_2:Vec<u32>) -> (u32, u32){
    if n==1{
        let pop1:u32 = initial[0];
        let pop2:u32 = initial[1];
        (pop1, pop2)
    }
    else{
        let pop1:u32 = population_1.last().unwrap().clone();
        let pop2:u32 = population_2.last().unwrap().clone();
        (pop1, pop2)
    }
    
}

fn update_simulation(pop1:u32, pop2:u32, r:f32, k:u32, compet:f32) -> f32 {
    let pop_1_fl:f32 = pop1 as f32;
    let pop_2_fl:f32 = pop2 as f32;
    let k_fl:f32 = k as f32;
    let competition_component = compet*pop_2_fl/k_fl;
    let delta_pop:f32 = r*pop_1_fl*(1.0-(pop_1_fl/k_fl)-competition_component);
    let new_pop:f32 = pop_1_fl + delta_pop;
    new_pop
}

fn check_extinction(pop:i32)->u32{
    if pop < 0{
        let pos_pop:u32 = 0;
        pos_pop
    }
    else{
        let pos_pop:u32 = pop as u32;
        pos_pop
    }
}


fn main() {
    //needs to add some populations prints
    //Parameters initialization
    //initial populations variable, vectore with initial pop for species 1 and for species 2
    let mut initial = Vec::new();
    initial.push(20);
    initial.push(20);

    //# of iteration
    let n_iter:u32 = 100;
   
    //r0 for species 1 and two
    let mut r = Vec::<f32>::new();
    r.push(0.6);
    r.push(0.8);

    //carrying capacity for species 1 and 2
    let mut k = Vec::<u32>::new();
    k.push(200);
    k.push(200);

    //competition effect of species 1 on 2 and 2 on 1 respectively
    let mut competition = Vec::<f32>::new();
    competition.push(0.7);
    competition.push(0.4);

    let _x = run_simulation(initial, n_iter, r, k, competition);
}
