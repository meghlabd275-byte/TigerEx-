from fastapi import FastAPI, HTTPException
from datetime import datetime, timedelta
from typing import Dict, List, Optional

app = FastAPI(title="TigerEx DAO Governance Service")

# DAO State
dao_state = {
    'proposals': [],
    'votes': defaultdict(list),
    'governance_token_holders': {},
    'treasury': {
        'total_funds': 1000000,  # TIGER tokens
        'allocated_funds': 0,
        'available_funds': 1000000
    },
    'governance_params': {
        'min_tokens_to_propose': 1000,
        'voting_period_days': 7,
        'quorum_percentage': 10,
        'pass_threshold': 51
    }
}

class DAOEngine:
    def __init__(self):
        self.proposal_counter = 0
        self.vote_counter = 0
    
    def create_proposal(self, proposer: str, title: str, description: str, 
                       proposal_type: str, parameters: Dict) -> Dict:
        """Create a new governance proposal"""
        self.proposal_counter += 1
        
        proposal = {
            'id': self.proposal_counter,
            'proposer': proposer,
            'title': title,
            'description': description,
            'type': proposal_type,
            'parameters': parameters,
            'status': 'ACTIVE',
            'created_at': datetime.utcnow(),
            'voting_end': datetime.utcnow() + timedelta(days=7),
            'votes_for': 0,
            'votes_against': 0,
            'votes_abstain': 0,
            'total_votes': 0,
            'quorum_reached': False,
            'passed': False
        }
        
        dao_state['proposals'].append(proposal)
        return proposal
    
    def cast_vote(self, voter: str, proposal_id: int, vote: str, voting_power: int) -> Dict:
        """Cast a vote on a proposal"""
        proposal = next((p for p in dao_state['proposals'] if p['id'] == proposal_id), None)
        
        if not proposal:
            raise HTTPException(status_code=404, detail="Proposal not found")
        
        if proposal['status'] != 'ACTIVE':
            raise HTTPException(status_code=400, detail="Proposal voting has ended")
        
        if datetime.utcnow() > proposal['voting_end']:
            raise HTTPException(status_code=400, detail="Voting period has expired")
        
        # Check if voter has already voted
        existing_vote = next((v for v in dao_state['votes'][proposal_id] if v['voter'] == voter), None)
        if existing_vote:
            raise HTTPException(status_code=400, detail="Already voted on this proposal")
        
        # Record vote
        vote_record = {
            'voter': voter,
            'proposal_id': proposal_id,
            'vote': vote,
            'voting_power': voting_power,
            'timestamp': datetime.utcnow()
        }
        
        dao_state['votes'][proposal_id].append(vote_record)
        
        # Update proposal vote counts
        if vote == 'FOR':
            proposal['votes_for'] += voting_power
        elif vote == 'AGAINST':
            proposal['votes_against'] += voting_power
        elif vote == 'ABSTAIN':
            proposal['votes_abstain'] += voting_power
        
        proposal['total_votes'] += voting_power
        
        # Check if quorum is reached
        total_supply = 10000000  # Total TIGER token supply
        quorum_tokens = total_supply * dao_state['governance_params']['quorum_percentage'] / 100
        
        if proposal['total_votes'] >= quorum_tokens:
            proposal['quorum_reached'] = True
        
        return vote_record
    
    def finalize_proposal(self, proposal_id: int) -> Dict:
        """Finalize a proposal and execute if passed"""
        proposal = next((p for p in dao_state['proposals'] if p['id'] == proposal_id), None)
        
        if not proposal:
            raise HTTPException(status_code=404, detail="Proposal not found")
        
        if proposal['status'] != 'ACTIVE':
            raise HTTPException(status_code=400, detail="Proposal already finalized")
        
        if datetime.utcnow() <= proposal['voting_end']:
            raise HTTPException(status_code=400, detail="Voting period still active")
        
        # Determine if proposal passed
        if proposal['quorum_reached']:
            for_votes = proposal['votes_for']
            against_votes = proposal['votes_against']
            total_votes = for_votes + against_votes
            
            if total_votes > 0:
                pass_percentage = (for_votes / total_votes) * 100
                if pass_percentage >= dao_state['governance_params']['pass_threshold']:
                    proposal['passed'] = True
                    proposal['status'] = 'PASSED'
                    # Execute proposal logic here
                    self.execute_proposal(proposal)
                else:
                    proposal['passed'] = False
                    proposal['status'] = 'REJECTED'
            else:
                proposal['passed'] = False
                proposal['status'] = 'REJECTED'
        else:
            proposal['passed'] = False
            proposal['status'] = 'FAILED_QUORUM'
        
        return proposal
    
    def execute_proposal(self, proposal: Dict):
        """Execute a passed proposal"""
        if proposal['type'] == 'PARAMETER_CHANGE':
            # Update governance parameters
            for param, value in proposal['parameters'].items():
                if param in dao_state['governance_params']:
                    dao_state['governance_params'][param] = value
        
        elif proposal['type'] == 'TREASURY_ALLOCATION':
            # Allocate treasury funds
            amount = proposal['parameters'].get('amount', 0)
            if amount <= dao_state['treasury']['available_funds']:
                dao_state['treasury']['allocated_funds'] += amount
                dao_state['treasury']['available_funds'] -= amount
        
        elif proposal['type'] == 'UPGRADE':
            # Schedule protocol upgrade
            print(f"Executing protocol upgrade: {proposal['title']}")
            # Implementation would go here

# API Endpoints
@app.post("/api/v1/dao/proposals")
async def create_proposal(proposal: Dict):
    """Create a new governance proposal"""
    engine = DAOEngine()
    new_proposal = engine.create_proposal(
        proposer=proposal['proposer'],
        title=proposal['title'],
        description=proposal['description'],
        proposal_type=proposal['type'],
        parameters=proposal['parameters']
    )
    
    return {
        "success": True,
        "proposal": new_proposal
    }

@app.post("/api/v1/dao/vote")
async def cast_vote(vote_data: Dict):
    """Cast a vote on a proposal"""
    engine = DAOEngine()
    vote = engine.cast_vote(
        voter=vote_data['voter'],
        proposal_id=vote_data['proposal_id'],
        vote=vote_data['vote'],
        voting_power=vote_data['voting_power']
    )
    
    return {
        "success": True,
        "vote": vote
    }

@app.post("/api/v1/dao/proposals/{proposal_id}/finalize")
async def finalize_proposal(proposal_id: int):
    """Finalize a proposal"""
    engine = DAOEngine()
    result = engine.finalize_proposal(proposal_id)
    
    return {
        "success": True,
        "proposal": result
    }

@app.get("/api/v1/dao/proposals")
async def get_proposals(status: str = "ALL"):
    """Get all proposals"""
    if status == "ALL":
        proposals = dao_state['proposals']
    else:
        proposals = [p for p in dao_state['proposals'] if p['status'] == status]
    
    return {
        "success": True,
        "proposals": proposals,
        "total_count": len(proposals)
    }

@app.get("/api/v1/dao/proposals/{proposal_id}")
async def get_proposal(proposal_id: int):
    """Get specific proposal details"""
    proposal = next((p for p in dao_state['proposals'] if p['id'] == proposal_id), None)
    
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")
    
    # Get votes for this proposal
    votes = dao_state['votes'].get(proposal_id, [])
    
    return {
        "success": True,
        "proposal": proposal,
        "votes": votes
    }

@app.get("/api/v1/dao/treasury")
async def get_treasury():
    """Get treasury information"""
    return {
        "success": True,
        "treasury": dao_state['treasury'],
        "governance_params": dao_state['governance_params']
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8298)
