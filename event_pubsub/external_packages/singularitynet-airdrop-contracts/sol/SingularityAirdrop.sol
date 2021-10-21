pragma solidity ^0.6.0;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/math/SafeMath.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";

contract SingularityAirdrop is Ownable, ReentrancyGuard {

    using SafeMath for uint256;

    ERC20 public airDropToken; // Address of token contract

    address public authorizer; // Authorizer Address for the airdrop 

    //To store the current air drop window claim period - There is no point storing all the airDrop window details in the structure
    uint256 public currentAirDropWindowId;
    uint256 public currentClaimStartTime;
    uint256 public currentClaimEndTime;

    //To store claimed signature from authorizer in order to prevent replay attack
    mapping (bytes32 => bool) public usedSignatures; 

    // Events
    event NewAuthorizer(address conversionAuthorizer);
    event WithdrawToken(address indexed owner, uint256 amount);
    event Claim(address indexed authorizer, address indexed claimer, uint256 amount, uint256 airDropId, uint256 airDropWindowId);

    constructor(address _token)
    public
    {
        airDropToken = ERC20(_token);
    }
    
    function updateAuthorizer(address newAuthorizer) public onlyOwner {

        require(newAuthorizer != address(0), "Invalid operator address");
        authorizer = newAuthorizer;

        emit NewAuthorizer(newAuthorizer);
    }


    function withdrawToken(uint256 value) public onlyOwner
    {

        // Check if contract is having required balance 
        require(airDropToken.balanceOf(address(this)) >= value, "Not enough balance in the contract");
        require(airDropToken.transfer(msg.sender, value), "Unable to transfer token to the operator account");

        emit WithdrawToken(msg.sender, value);
        
    }

    function configureAirDropClaim(uint256 airDropWindowId, uint256 claimStartTime, uint256 claimEndTime) public onlyOwner {

        // Check for the valid parameters
        require(airDropWindowId >= currentAirDropWindowId && claimStartTime > 0, "Invalid parameters");
        // Enabling a provision to update the Claim Period as it is going to done by owner only
        require(claimStartTime < claimEndTime && now < claimEndTime , "Invalid configurations");

        currentAirDropWindowId = airDropWindowId;
        currentClaimStartTime = claimStartTime;
        currentClaimEndTime = claimEndTime;

    }

    function claim(address token, uint256 amount, uint256 airDropId, uint256 airDropWindowId, uint8 v, bytes32 r, bytes32 s) external nonReentrant {
    
        // Check if contract is having required balance 
        require(airDropToken.balanceOf(address(this)) >= amount, "Not enough balance in the contract");

        // Restrict the claim time frame as per the claim period configured
        require(airDropWindowId == currentAirDropWindowId && now >= currentClaimStartTime && now <= currentClaimEndTime, "Invalid claim request");

        //compose the message which was signed
        bytes32 message = prefixed(keccak256(abi.encodePacked("__airdropclaim", amount, msg.sender, airDropId, airDropWindowId, this, token)));
        // check that the signature is from the authorizer
        address signAddress = ecrecover(message, v, r, s);
        require(signAddress == authorizer, "Invalid request or signature for claim");

        //check for replay attack (message signature can be used only once)
        require( ! usedSignatures[message], "Signature has already been used");
        usedSignatures[message] = true;

        // Transfer to User Wallet
        require(airDropToken.transfer(msg.sender, amount), "Unable to transfer token to the account");

        emit Claim(authorizer, msg.sender, amount, airDropId, airDropWindowId);

    }

    /// builds a prefixed hash to mimic the behavior of ethSign.
    function prefixed(bytes32 hash) internal pure returns (bytes32) 
    {
        return keccak256(abi.encodePacked("\x19Ethereum Signed Message:\n32", hash));
    }



}