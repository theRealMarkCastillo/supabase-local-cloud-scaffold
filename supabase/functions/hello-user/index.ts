// The default JWT policy is only the first check: verify the caller's user identity.
const origin = new URL(Deno.env.get('SUPABASE_PUBLIC_URL')!).origin;
const cors = {'Access-Control-Allow-Origin':origin, 'Access-Control-Allow-Headers':'authorization, apikey, content-type, x-client-info', 'Access-Control-Allow-Methods':'POST, OPTIONS', 'Vary':'Origin'};
Deno.serve(async (request) => {
  if (request.method === 'OPTIONS') return new Response(null,{status:204,headers:cors});
  const respond = (body:unknown,status=200) => Response.json(body,{status,headers:cors});
  if (request.method !== 'POST') return respond({error:'POST required'},405);
  const authorization=request.headers.get('authorization') || '';
  const identity=await fetch(Deno.env.get('SUPABASE_URL')+'/auth/v1/user',{headers:{apikey:Deno.env.get('SUPABASE_ANON_KEY')!,authorization}});
  if (!identity.ok) return respond({error:'Sign in first'},401);
  const user=await identity.json();
  return respond({message:'Hello from your function',user_id:user.id});
});
