import time
import sys
import dns.resolver
import multiprocessing

def get_domain_controllers(domain):
    try:
#      print(f"Resolving _ldap._tcp.dc._msdcs.{domain}")
      # Create a resolver object
      resolver = dns.resolver.Resolver()
      # Set the timeout to 5 seconds
      resolver.lifetime = 3
      srv_records = resolver.resolve("_ldap._tcp.dc._msdcs." + domain, 'SRV')
      domain_controllers = []
      for srv in srv_records:
          domain_controllers.append(str(srv.target).rstrip('.'))
      print(f"[+] Received SRV records {domain_controllers}")
      return domain_controllers
    except dns.resolver.NXDOMAIN:
      print(f"[-] Could not find SRV record for {domain} (NXDOMAIN)")
    except dns.resolver.NoAnswer:
      print(f"[-] Could not find SRV record for {domain} (NoAnswer)")
    except dns.resolver.NoNameservers:
      print(f"[-] Could not find SRV record for {domain} (No NS)")
    except dns.resolver.LifetimeTimeout:
      print(f"[-] Hit timeout, need to sleep a little. Sleeping 6s")
      time.sleep(6)
    return None

def lookup_domain(domainToCheck, addomain):
    addomain = addomain.replace("\x013","")
    domain_controllers = get_domain_controllers(addomain)
    #print(f"Checking {domain_controllers}")
    if domain_controllers is None:
      return None
    for dc in domain_controllers:
        #print(f"Found SRV record {dc}")
        try:
            answers = dns.resolver.resolve(domainToCheck, 'A', raise_on_no_answer=False)
            if answers:
                for answer in answers:
                    print(f"[+] {addomain} SRV ({dc}) resolved {domainToCheck} to {answer}")
            else:
                print(f"[-] {dc} could not resolve {domainToCheck}")
        except dns.resolver.NXDOMAIN:
            print(f"[-] {dc} could not resolve {domainToCheck}")


# Open the file on disk
with open("domains.txt", "r") as file:
    # threads
    processes = []

    # Iterate over each line in the file
    for line in file:
        # Remove any trailing newline characters
        line = line.strip()

        # Call the lookup_domain function with the modified argument
        process = multiprocessing.Process(target=lookup_domain, args=("fooo.daloo.de", line))
        process.start()
        processes.append(process)

        while len(multiprocessing.active_children()) >= 50:
            # Wait for running processes to finish
            time.sleep(1)
        processes = [p for p in processes if p.is_alive()]
        # Wait for all processes to finish
        for process in processes:
            process.join()
#lookup_domain("fooo.daloo.de", sys.argv[1])
