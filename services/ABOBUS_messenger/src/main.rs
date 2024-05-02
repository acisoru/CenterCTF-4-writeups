#![allow(unused_variables, non_snake_case)]
pub mod user;
pub mod storage;

use storage::File;
use user::Person;
use rand::Rng;
use std::io;
use rusqlite::{Connection, Result };
use base64::{engine::general_purpose::STANDARD, Engine as _};
use std::io::Write;
use bulletproofs::{inner_product_proof::InnerProductProof, util, BulletproofGens, inner_product_proof::inner_product};
use merlin::Transcript;
use core::iter;
use sha2::{Sha512,Digest};
use rand;
use serpent;
use curve25519_dalek::{ristretto::CompressedRistretto, RistrettoPoint, scalar::Scalar, traits::VartimeMultiscalarMul,digest::Update};

fn parse_proof(proof: Vec<u8>) -> Result<(RistrettoPoint, InnerProductProof), String>{
    let P = match CompressedRistretto::from_slice(&proof[..32]){
        Err(e) => return Err("parse error".to_string()),
        Ok(v) => match v.decompress(){
            None =>  return Err("parse error".to_string()),
            Some(v) => v
        }
    };
    let res_proof = match InnerProductProof::from_bytes(&proof[32..]){
        Err(e) => return Err("parse error".to_string()),
        Ok(v) => v
    };
    Ok((P, res_proof))
}
fn main() {
    let secret = Scalar::from_bytes_mod_order(include_bytes!("secret_key").clone());
    let stdin = io::stdin();
    let mut rng = rand::thread_rng();
    let mut conn = Connection::open("cats.db").unwrap();
    let dimension = 4;
    let mut person: Person = Person{id: 1337, description:String::new(),username:String::new(),private_key: [0u8;16], is_logined:false};

    macro_rules! read_line {
        ( $var:ident ) => {
            stdin.read_line(&mut $var).unwrap();
            $var.pop()
        };
    }

    let bp_gens = BulletproofGens::new(dimension, 1);
    let G: Vec<RistrettoPoint> = bp_gens.share(0).G(dimension).cloned().collect();
    let H: Vec<RistrettoPoint> = bp_gens.share(0).H(dimension).cloned().collect();
    
    let G_factors: Vec<Scalar> = iter::repeat(Scalar::ONE).take(dimension).collect();

    loop {
        let mut command = String::new();
        print!("Choose option:\n- register\n- login\n- profile_description\n- upload_file\n- get_encrypted_file\n- get_decrypted_file\n- list_files\n- logout\n");
        read_line!(command);

        match command.as_str(){
            "register" => {
                if person.is_logined{
                    println!("Logout first :(");
                    continue;
                }
                print!("Username: ");
                io::stdout().flush();
                let mut username = String::new();
                read_line!(username);

                print!("Profile description: ");
                io::stdout().flush();
                let mut description = String::new();
                read_line!(description);

                let mut private_key = [0u8;16];
                rng.fill(&mut private_key);
                match Person::new(&mut conn, &username, &private_key, &description){
                    Err(msg) => {
                        println!("already exists ;(");
                        continue;
                    }
                    _ => ()
                }
                
                let Q = RistrettoPoint::hash_from_bytes::<Sha512>(username.as_bytes());
                let key = Sha512::new().chain(&username).chain(secret.to_bytes());
                let mut verifier = Transcript::new(username.leak().as_bytes());
                let y_inv = Scalar::from_hash(key);
                let H_factors: Vec<Scalar> = util::exp_iter(y_inv).take(dimension).collect();
                

                let a: Vec<_> = (0..dimension).map(|_| Scalar::random(&mut rng)).collect();
                let b: Vec<_> = (0..dimension).map(|_| Scalar::random(&mut rng)).collect();
                let c = inner_product(&a, &b);
                
                let b_prime = b.iter().zip(util::exp_iter(y_inv)).map(|(bi, yi)| bi * yi);
                // a.iter() has Item=&Scalar, need Item=Scalar to chain with b_prime
                let a_prime = a.iter().cloned();
        
                let P = RistrettoPoint::vartime_multiscalar_mul(
                    a_prime.chain(b_prime).chain(iter::once(c)),
                    G.iter().chain(H.iter()).chain(iter::once(&Q)),
                );

                let proof = InnerProductProof::create(
                    &mut verifier,
                    &Q,
                    &G_factors,
                    &H_factors,
                    G.clone(),
                    H.clone(),
                    a.clone(),
                    b.clone(),
                ).to_bytes();
                let proof_bytes: Vec<u8> = P.compress().to_bytes().into_iter().chain(proof.into_iter()).collect();

                println!("here is your proof: {}", STANDARD.encode(proof_bytes));
                println!("registered successfully\n");

            }
            "login" => {
                print!("Username: ");
                io::stdout().flush();
                
                let mut username: String = String::new();
                read_line!(username);
                
                print!("proof: ");
                io::stdout().flush();
                
                let mut proof_st = String::new();
                read_line!(proof_st);

                let bytes = match STANDARD.decode(&proof_st){
                    Err(e) => {println!("Invalid proof encoding\n"); continue;}
                    Ok(v) =>v
                };
                let (P,proof) = match parse_proof(bytes){
                    Err(e) => {
                        println!("invalid proof format");
                        continue;
                    }
                    Ok(v) => v
                };

                let Q = RistrettoPoint::hash_from_bytes::<Sha512>(username.as_bytes());
                let key = Sha512::new().chain(&username).chain(secret.to_bytes());
                let mut verifier = Transcript::new(username.clone().leak().as_bytes());
                let y_inv = Scalar::from_hash(key);
                let H_factors: Vec<Scalar> = util::exp_iter(y_inv).take(dimension).collect();

                match proof.verify(
                        dimension,
                        &mut verifier,
                        &G_factors,
                        &H_factors,
                        &P,
                        &Q,
                        &G,
                        &H
                ){
                    Ok(v) => {println!("successful login!\n");}
                    Err(e) => {println!("login error: {}", e); continue}
                }
                
                match Person::get_by_username(&mut conn, &username){
                    Err(e) => {println!("wtf error"); continue;}
                    Ok(v) => {person = v;}
                };
                person.is_logined = true;
            }
            "logout" => {
                println!("successful logout!\n");
                person.is_logined = false;
            }
            "profile_description" => {
                if !person.is_logined{
                    println!("Login first :(");
                    continue;
                }
                println!("{} Description:" ,person.username);
                println!("{}\n",person.description);
            }
            "upload_file" => {
                if !person.is_logined{
                    println!("Login first :(");
                    continue;
                }
                print!("Enter file content: ");
                io::stdout().flush();
                let mut content = String::new();
                read_line!(content);
        
                content.push_str(" ".repeat(16-(content.len()%16)).as_str());
                let encrypted = serpent::encrypt_blocks(&person.private_key,content.as_bytes());
                match File::create(&mut conn, person.id,&encrypted){
                    Ok(v) => {println!("Uploaded successfully!");println!("Your file_id: {v}\n");}
                    Err(e) => {println!("some err in sql: {e}");continue;}
                };
                
            }
            "get_encrypted_file" => {
                if !person.is_logined{
                    println!("Login first :(");
                    continue;
                }

                print!("Enter file_id: ");
                io::stdout().flush();
                let mut file_id = String::new();
                read_line!(file_id);
                
                let file = match File::get_by_id(&mut conn, match file_id.parse::<u32>(){
                    Err(e) => {println!("INPUT NUMBER WAAAAA"); continue;}
                    Ok(v) => v
                }){
                    Err(e) => {println!("Some sql error happen"); continue;}
                    Ok(v) => v
                };
                println!("Encrypted file content: {:?}\n", file.content);
            }
            "get_decrypted_file" => {
                if !person.is_logined{
                    println!("Login first :(");
                    continue;
                }

                print!("Enter file_id: ");
                io::stdout().flush();
                let mut file_id = String::new();
                read_line!(file_id);
                
                let file = match File::get_by_id(&mut conn, match file_id.parse::<u32>(){
                    Err(e) => {println!("INPUT NUMBER WAAAAA"); continue;}
                    Ok(v) => v
                }){
                    Err(e) => {println!("Some sql error happen"); continue;}
                    Ok(v) => v
                };
                let decrypted = serpent::decrypt_blocks(&person.private_key, file.content.as_slice());
                println!("Decrypted file content: {:?}\n", match String::from_utf8(decrypted){
                    Err(e) => {println!("[ERROR] cannot decrypt string\n"); continue;}
                    Ok(v) =>v
                });
            }
            "list_files" => {
                if !person.is_logined{
                    println!("Login first :(");
                    continue;
                }
                println!("Your files:");
                let list  = match File::list(&mut conn,person.id){
                    Ok(v) => v,
                    Err(e) => {println!("some err in sql: {e}");continue;}
                };
                for file in list{
                    println!("file_id: {}", file.file_id);
                    let decrypted = serpent::decrypt_blocks(&person.private_key, file.content.as_slice());
                    println!("file_content: {}",match String::from_utf8(decrypted){
                        Err(e) => {println!("[ERROR] cannot decrypt string\n"); continue;}
                        Ok(v) =>v
                    });
                }
                println!("");
            }
            
            _ => {
                println!("invalid command");
            }
        }
    }
}
