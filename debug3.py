import re

encoded = "%7B%22action%22%3A%22create%22%2C%22alert%22%3A%7B%22id%22%3A6784316513%2C%22number%22%3A72%2C%22state%22%3A%22open%22%2C%22node_id%22%3A%22RVA_kwDORElxzc8AAAABlGB0YQ%22%2C%22affected_range%22%3A%22%3C+0.0.27%22%2C%22affected_package_name%22%3A%22python-multipart%22%2C%22external_reference%22%3A%22https%3A%2F%2Fgithub.com%2Fadvisories%2FGHSA-pp6c-gr5w-3c5g%22%2C%22external_identifier%22%3A%22CVE-2026-42561%22%2C%22ghsa_id%22%3A%22GHSA-pp6c-gr5w-3c5g%22%2C%22severity%22%3A%22high%22%2C%22created_at%22%3A%222026-05-08T11%3A25%3A28Z%22%2C%22fixed_in%22%3A%220.0.27%22%7D%2C%22repository%22%3A%7B%22id%22%3A1145663949%2C%22node_id%22%3A%22R_kgDORElxzQ%22%2C%22name%22%3A%22chronos-AI-agent-builder-studio%22%2C%22full_name%22%3A%22Chronos-llc%2Fchronos-AI-agent-builder-studio%22%2C%22private%22%3Afalse%2C%22owner%22%3A%7B%22login%22%3A%22Chronos-llc%22%2C%22id%22%3A258978628%2C%22node_id%22%3A%22O_kgDOD2-zRA%22%2C%22avatar_url%22%3A%22https%3A%2F%2Favatars.githubusercontent.com%2Fu%2F258978628%3Fv%3D4%22%2C%22gravatar_id%22%3A%22%22%2C%22url%22%3A%2A%2F%2Fapi.github.com%2Fusers%2FChronos-llc%22%2C%22html_url%22%3A%22https%3A%2F%2Fgithub.com%2FChronos-llc%22%2C%22type%22%3A%22Organization%22%2C%22site_admin%22%3Afalse%7D"

# Find the owner url field
pattern = r'%22url%22%3A%2A%2F%2F[^%]*%22'
match = re.search(pattern, encoded)
if match:
    print("Found url field pattern:")
    print("Full match:", match.group())
    print("Start:", match.start(), "End:", match.end())
    print("\n50 chars before:", encoded[max(0,match.start()-50):match.start()])
    print("50 chars after:", encoded[match.end():match.end()+50])
else:
    print("Pattern not found with %2A%2F%2F")
    # Try to find any url field
    idx = encoded.find('%22url%22%3A')
    if idx >= 0:
        print(f"Found %22url%22%3A at {idx}")
        print("Context:", encoded[idx:idx+100])
