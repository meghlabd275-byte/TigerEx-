package com.tigerex.users.app.ui.fragments

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.fragment.app.Fragment
import androidx.lifecycle.ViewModelProvider
import androidx.recyclerview.widget.LinearLayoutManager
import com.tigerex.users.app.databinding.FragmentHomeBinding
import com.tigerex.users.app.ui.adapters.WatchlistAdapter
import com.tigerex.users.app.ui.screens.*

class HomeFragment : Fragment() {
    
    private var _binding: FragmentHomeBinding? = null
    private val binding get() = _binding!!
    
    private lateinit var viewModel: MainViewModel
    private lateinit var watchlistAdapter: WatchlistAdapter
    
    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentHomeBinding.inflate(inflater, container, false)
        return binding.root
    }
    
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        viewModel = ViewModelProvider(requireActivity())[MainViewModel::class.java]
        
        setupUI()
        setupClickListeners()
        observeData()
    }
    
    private fun setupUI() {
        watchlistAdapter = WatchlistAdapter { coin ->
            viewModel.selectCoin(coin)
        }
        
        binding.recyclerWatchlist.apply {
            layoutManager = LinearLayoutManager(context)
            adapter = watchlistAdapter
        }
    }
    
    private fun setupClickListeners() {
        binding.apply {
            // Quick Actions
            cardBuy.setOnClickListener { navigateTo(TradeScreen::class.java) }
            cardSell.setOnClickListener { navigateTo(TradeScreen::class.java) }
            cardSend.setOnClickListener { navigateTo(WalletScreen::class.java) }
            cardConvert.setOnClickListener { navigateTo(ConvertScreen::class.java) }
            
            // Service Cards
            cardP2P.setOnClickListener { navigateTo(P2PScreen::class.java) }
            cardDeposit.setOnClickListener { navigateTo(DepositScreen::class.java) }
            cardWithdraw.setOnClickListener { navigateTo(WithdrawScreen::class.java) }
            cardFutures.setOnClickListener { navigateTo(FuturesScreen::class.java) }
            cardStaking.setOnClickListener { navigateTo(StakingScreen::class.java) }
            cardLaunchpool.setOnClickListener { navigateTo(LaunchpoolScreen::class.java) }
            cardCopyTrading.setOnClickListener { navigateTo(CopyTradingScreen::class.java) }
            cardMining.setOnClickListener { navigateTo(MiningScreen::class.java) }
            cardCard.setOnClickListener { navigateTo(CardScreen::class.java) }
            cardRedpacket.setOnClickListener { navigateTo(RedpacketScreen::class.java) }
            cardReferral.setOnClickListener { navigateTo(ReferralScreen::class.java) }
            cardMegadrop.setOnClickListener { navigateTo(MegadropScreen::class.java) }
            cardIDO.setOnClickListener { navigateTo(IDOScreen::class.java) }
            cardAirdrop.setOnClickListener { navigateTo(AirdropScreen::class.java) }
            
            // Top Bar
            iconNotifications.setOnClickListener { navigateTo(NotificationsScreen::class.java) }
            iconSettings.setOnClickListener { navigateTo(SettingsScreen::class.java) }
            iconSupport.setOnClickListener { navigateTo(SupportScreen::class.java) }
        }
    }
    
    private fun observeData() {
        viewModel.portfolio.observe(viewLifecycleOwner) { portfolio ->
            binding.apply {
                textTotalBalance.text = portfolio.totalBalance
                textPnl24h.text = portfolio.pnl24h
                textPnl24h.setTextColor(
                    if (portfolio.isPositive) resources.getColor(com.tigerex.users.app.R.color.success, null)
                    else resources.getColor(com.tigerex.users.app.R.color.error, null)
                )
            }
        }
        
        viewModel.watchlist.observe(viewLifecycleOwner) { coins ->
            watchlistAdapter.submitList(coins)
        }
    }
    
    private fun navigateTo(screen: Class<*>) {
        // Navigation code
    }
    
    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}